from groq import Groq
from typing import Dict, Tuple
from dataclasses import dataclass
import json
import re
import logging
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@dataclass
class TransformerConfig:
    """Configuration for the article transformer"""
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.1
    max_tokens: int = 500
    retry_attempts: int = 3
    default_threshold: float = 0.3
    max_text_length: int = 2000


class ArticleTransformer:
    """
    Transform articles by generating summaries and classifications using Groq's Llama 3.1 8B.
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
        self.logger.info(f"Initializing ArticleTransformer with {self.config.model}...")

        self.client = Groq(api_key=api_key)

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_api(self, prompt: str) -> str:
        """Call Groq API with retry logic."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            self.logger.error(f"API call failed: {e}")
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

    def _parse_response(self, output: str, threshold: float, original_title: str) -> Tuple[str, str, str]:
        """Parse API response and extract title, summary, category."""
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
                bullets_match = re.search(r'"bullets"\s*:\s*"([^"]+)"', output)
                summary_match = re.search(r'"summary"\s*:\s*"([^"]+)"', output)
                category_match = re.search(r'"category"\s*:\s*"([^"]+)"', output)

                if all([title_match, bullets_match, summary_match, category_match]):
                    return (
                        title_match.group(1)[:100],
                        bullets_match.group(1),
                        summary_match.group(1)[:1000],
                        self._validate_category(category_match.group(1))
                    )
            except Exception as e:
                self.logger.error(f"Regex extraction failed: {e}")

        # Return defaults if all parsing fails
        self.logger.error("All parsing strategies failed, returning defaults")
        return original_title, "Unable to generate summary", "General"

    def transform(self, title: str, article_text: str, threshold: float = None) -> Tuple[str, str, str, str]:
        """
        Transform an article by generating title, summary, and category.

        Args:
            title: The article title
            article_text: The article text content
            threshold: Confidence threshold for classification (optional)

        Returns:
            Tuple of (title, article_summary, category)
        """
        if threshold is None:
            threshold = self.config.default_threshold

        try:
            # Preprocess text
            cleaned_text = self._preprocess_text(article_text)
            cleaned_title = self._preprocess_text(title)

            # Build prompt
            prompt = self._build_prompt(cleaned_title, cleaned_text, threshold)

            # Call API
            raw_output = self._call_api(prompt)

            # Parse and return
            result_title, bullets, summary, category = self._parse_response(raw_output, threshold, cleaned_title)

            self.logger.info(f"Transformed: {category}")
            return result_title, bullets, summary, category

        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            # Return original title with error info
            return title, f"Error generating summary: {str(e)}", "General"