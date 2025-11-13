from groq import Groq
from typing import Dict, Tuple, List
from dataclasses import dataclass
import json
import re
import logging
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@dataclass
class TransformerConfig:
    """Configuration for the article transformer"""
    models: List[str] = None  # List of models to rotate through
    temperature: float = 0.1
    max_tokens: int = 500
    retry_attempts: int = 3
    default_threshold: float = 0.3
    max_text_length: int = 2000
    enable_model_rotation: bool = True  # Enable/disable model rotation

    def __post_init__(self):
        """Set default models if not provided"""
        if self.models is None:
            self.models = [
                # Tier 1: High volume, fast (14.4K RPD)
                "llama-3.1-8b-instant",

                # Tier 2: Newer Llama 4 models (likely 1K RPD)
                "meta-llama/llama-4-maverick-17b-128e-instruct",

                # Tier 3: High quality (1K RPD)
                "llama-3.3-70b-versatile",
                "qwen/qwen3-32b",

                # Tier 4: Unlimited tokens fallback (250 RPD)
                "groq/compound",
                "groq/compound-mini",

                # Tier 5: Additional alternatives
                "allam-2-7b",
                "moonshotai/kimi-k2-instruct",
                "openai/gpt-oss-20b"
            ]


class ArticleTransformer:
    """
    Transform articles by generating summaries and classifications using Groq's LLM.
    Implements automatic model rotation to avoid rate limits.
    """

    def __init__(self, api_key: str = None, config: TransformerConfig = None):
        """
        Initialize the transformer with Groq API key.

        Args:
            api_key: Your Groq API key (if None, will try to get from GROQ_API_KEY env variable)
            config: Optional configuration object
        """
        # Handle API key - try parameter first, then environment variable
        if api_key is None:
            api_key = os.environ.get('GROQ_API_KEY')

        if not api_key:
            raise ValueError("API key is required. Provide it as parameter or set GROQ_API_KEY environment variable.")

        self.logger = logging.getLogger(__name__)

        self.config = config or TransformerConfig()
        self.client = Groq(api_key=api_key)

        # Model rotation state
        self.current_model_index = 0
        self.model_failures = {model: 0 for model in self.config.models}
        self.model_last_used = {model: 0 for model in self.config.models}
        self.total_api_calls = 0
        self.successful_calls_by_model = {model: 0 for model in self.config.models}

        self.logger.info(f"Initializing ArticleTransformer with {len(self.config.models)} models")
        self.logger.info(f"Model rotation: {self.config.enable_model_rotation}")
        self.logger.info(f"Available models: {', '.join(self.config.models)}")

        # Define categories
        self.categories = [
            "M&A",
            "Spin offs",
            "Buybacks",
            "Guidance",
            "Leadership",
            "Approvals",
            "Activism",
            "General"
        ]

        self.category_descriptions = {
            "M&A": "mergers, acquisitions, deals, takeovers, purchases, buying companies",
            "Spin offs": "spin-offs, carve-outs, separating business units, splitting companies",
            "Buybacks": "share buybacks, stock repurchases, dividend payments, shareholder returns",
            "Guidance": "earnings guidance, financial forecasts, preliminary results, outlook, pre-announcements",
            "Leadership": "CEO appointments, executive changes, board members, management transitions",
            "Approvals": "FDA approvals, drug approvals, product launches, regulatory approvals",
            "Activism": "activist investors, shareholder activism, proxy fights, corporate governance",
            "General": "business updates, partnerships, product announcements, or other topics"
        }

        self.logger.info("ArticleTransformer ready!")

    def _preprocess_text(self, text: str) -> str:
        """Clean and truncate text for optimal processing."""
        if not text or not isinstance(text, str):
            return ""

        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Truncate if too long
        if len(text) > self.config.max_text_length:
            self.logger.warning(f"Text truncated from {len(text)} to {self.config.max_text_length} characters")
            text = text[:self.config.max_text_length]

        return text

    def _build_prompt(self, title: str, text: str, threshold: float) -> str:
        """Build the transformation prompt."""
        labels = [f"  - {cat}: {desc}" for cat, desc in self.category_descriptions.items()]
        labels_str = "\n".join(labels)

        prompt = f"""You are an expert financial analyst at Bloomberg specializing in press release analysis.

Analyze the following press release and provide:
1. A REFINED TITLE (maximum 10 words) - improve the existing title if needed
2. TWO BULLET POINTS (maximum 10 words each) - extract the two most important points from the article and create concise bullet points for each, elaborate beyond the title here
3. A JARGON-FREE SUMMARY (maximum 300 words) - explain in plain English, elaborate beyond the bullet points here
4. CATEGORY - the single most relevant category from the list below
5. CONFIDENCE - How confident are you on a scale of 0.0 to 1.0 with the category assigned for the article.

CATEGORIES:
{labels_str}

CLASSIFICATION RULES:
- Only assign a specific category if confidence is >= {threshold}
- If uncertain, use "General"

ARTICLE TITLE: {title}

ARTICLE TEXT:
{text}

Respond ONLY with valid JSON:
{{
  "title": "Refined title here",
  "bullets": ["bullet point 1", "bullet point 2"],
  "summary": "Plain English explanation of the article",
  "category": "exact category name from list above",
  "confidence": 0.95
}}"""

        return prompt

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error"""
        error_str = str(error).lower()
        return any(indicator in error_str for indicator in [
            'rate limit',
            'rate_limit',
            'ratelimit',
            '429',
            'too many requests',
            'quota exceeded'
        ])

    def _get_next_model(self) -> str:
        """Get the next model in rotation"""
        if not self.config.enable_model_rotation:
            return self.config.models[0]

        # Move to next model
        self.current_model_index = (self.current_model_index + 1) % len(self.config.models)
        next_model = self.config.models[self.current_model_index]

        self.logger.info(f"Switching to model: {next_model}")
        return next_model

    def _call_api_with_rotation(self, prompt: str) -> Tuple[str, str]:
        """
        Call Groq API with model rotation on rate limits.

        Returns:
            Tuple of (response_text, model_used)
        """
        models_tried = set()
        last_error = None

        # Try each model in rotation
        while len(models_tried) < len(self.config.models):
            current_model = self.config.models[self.current_model_index]

            if current_model in models_tried:
                # Tried all models, break
                break

            models_tried.add(current_model)

            try:
                self.logger.info(f"Attempting API call with model: {current_model}")

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )

                # Success!
                self.total_api_calls += 1
                self.successful_calls_by_model[current_model] += 1
                self.model_last_used[current_model] = time.time()

                self.logger.info(
                    f"✓ Success with {current_model} (Total calls: {self.successful_calls_by_model[current_model]})")

                return response.choices[0].message.content.strip(), current_model

            except Exception as e:
                last_error = e
                self.model_failures[current_model] += 1

                if self._is_rate_limit_error(e):
                    self.logger.warning(f"⚠ Rate limit hit for {current_model}: {str(e)[:100]}")

                    if self.config.enable_model_rotation and len(models_tried) < len(self.config.models):
                        self.logger.info(f"Rotating to next model...")
                        self._get_next_model()
                        time.sleep(1)  # Brief pause before trying next model
                        continue
                    else:
                        self.logger.error("All models rate limited or rotation disabled")
                        raise
                else:
                    # Non-rate-limit error, log and raise
                    self.logger.error(f"✗ API call failed with {current_model}: {e}")
                    raise

        # If we exhausted all models
        self.logger.error(f"All {len(self.config.models)} models failed or rate limited")
        raise last_error if last_error else Exception("All models unavailable")

    def _call_api(self, prompt: str) -> str:
        """Call Groq API with retry logic and model rotation."""
        try:
            response_text, model_used = self._call_api_with_rotation(prompt)
            return response_text
        except Exception as e:
            self.logger.error(f"API call failed after trying all models: {e}")
            raise

    def _validate_category(self, category: str) -> str:
        """Ensure returned category is valid."""
        if category in self.categories:
            return category

        # Case-insensitive match
        category_lower = category.lower()
        for valid_cat in self.categories:
            if valid_cat.lower() == category_lower:
                return valid_cat

        # Default to General
        self.logger.warning(f"Unknown category '{category}', defaulting to 'General'")
        return "General"

    def _parse_response(self, output: str, threshold: float, original_title: str) -> Tuple[str, List[str], str, str]:
        """Parse API response and extract title, bullets, summary, category."""
        try:
            # Remove markdown code blocks if present
            cleaned = re.sub(r'```json\s*|\s*```', '', output)
            parsed = json.loads(cleaned)

            title = parsed.get('title', original_title)[:100]
            bullets = parsed.get('bullets', [])
            summary = parsed.get('summary', 'No summary available')[:1000]
            category = self._validate_category(parsed.get('category', 'General'))
            confidence = float(parsed.get('confidence', 0.5))

            # Apply threshold logic
            if confidence < threshold and category != "General":
                self.logger.info(f"Confidence {confidence} below threshold {threshold}, using 'General'")
                category = "General"

            return title, bullets, summary, category

        except json.JSONDecodeError:
            self.logger.warning("JSON parsing failed, trying regex extraction")

            # Try regex extraction
            try:
                title_match = re.search(r'"title"\s*:\s*"([^"]+)"', output)
                bullets_match = re.search(r'"bullets"\s*:\s*\[([^\]]+)\]', output)
                summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', output)
                category_match = re.search(r'"category"\s*:\s*"([^"]+)"', output)

                if all([title_match, summary_match, category_match]):
                    # Extract bullets from array string
                    bullets = []
                    if bullets_match:
                        bullets_str = bullets_match.group(1)
                        bullets = [b.strip(' "') for b in bullets_str.split(',')]

                    return (
                        title_match.group(1)[:100],
                        bullets if bullets else [],
                        summary_match.group(1)[:1000],
                        self._validate_category(category_match.group(1))
                    )
            except Exception as e:
                self.logger.error(f"Regex extraction failed: {e}")

        # Return defaults if all parsing fails
        self.logger.error("All parsing strategies failed, returning defaults")
        return original_title, [], "Unable to generate summary", "General"

    def transform(self, title: str, article_text: str, threshold: float = None) -> Tuple[str, List[str], str, str]:
        """
        Transform an article by generating title, bullets, summary, and category.

        Args:
            title: The article title
            article_text: The article text content
            threshold: Confidence threshold for classification (optional)

        Returns:
            Tuple of (title, bullets, summary, category)
        """
        if threshold is None:
            threshold = self.config.default_threshold

        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(article_text)
            cleaned_title = self._preprocess_text(title)

            # Build prompt
            prompt = self._build_prompt(cleaned_title, cleaned_text, threshold)

            # Call API with model rotation
            raw_output = self._call_api(prompt)

            # Parse and return
            result_title, bullets, summary, category = self._parse_response(raw_output, threshold, cleaned_title)

            self.logger.info(f"Transformed: {category}")
            return result_title, bullets, summary, category

        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            # Return original title with error info
            return title, [], f"Error generating summary: {str(e)}", "General"

    def get_stats(self) -> Dict:
        """
        Get usage statistics including model rotation info.

        Returns:
            Dictionary with API usage and model statistics
        """
        return {
            'total_api_calls': self.total_api_calls,
            'current_model': self.config.models[self.current_model_index],
            'successful_calls_by_model': self.successful_calls_by_model,
            'model_failures': self.model_failures,
            'model_rotation_enabled': self.config.enable_model_rotation,
            'available_models': self.config.models
        }

    def reset_stats(self):
        """Reset all usage statistics"""
        self.total_api_calls = 0
        self.successful_calls_by_model = {model: 0 for model in self.config.models}
        self.model_failures = {model: 0 for model in self.config.models}
        self.model_last_used = {model: 0 for model in self.config.models}
        self.logger.info("Statistics reset")


# Example usage
if __name__ == "__main__":
    # Initialize with model rotation enabled (default)
    config = TransformerConfig(
        enable_model_rotation=True,
        models=[
            "llama-3.1-8b-instant",
            "meta-llama/llama-guard-4-12b",
            "groq/compound-mini"
        ]
    )

    transformer = ArticleTransformer(config=config)

    # Example article
    title = "Company Announces Acquisition"
    text = "Company X announced today that it will acquire Company Y for $1 billion..."

    # Transform
    result_title, bullets, summary, category = transformer.transform(title, text)

    print(f"Title: {result_title}")
    print(f"Bullets: {bullets}")
    print(f"Summary: {summary}")
    print(f"Category: {category}")

    # Check stats
    stats = transformer.get_stats()
    print(f"\nStats: {stats}")