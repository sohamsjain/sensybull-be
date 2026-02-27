from typing import Dict, Tuple, List
from dataclasses import dataclass
import json
import re
import logging

from .groq_client_pool import GroqClientPool


@dataclass
class TransformerConfig:
    """Configuration for the article transformer."""
    temperature: float = 0.1
    max_tokens: int = 1024
    default_threshold: float = 0.3
    max_text_length: int = 2000


# Aliases for backward compatibility with old category names
CATEGORY_ALIASES = {
    "spin offs": "Spin-offs",
    "spin-off": "Spin-offs",
    "spin off": "Spin-offs",
}


class ArticleTransformer:
    """
    Transform articles by generating summaries and classifications using Groq's LLM.
    Uses an injected GroqClientPool for API calls with automatic model rotation.
    """

    def __init__(self, groq_pool: GroqClientPool, config: TransformerConfig = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or TransformerConfig()
        self.groq_pool = groq_pool

        # Define expanded categories (15)
        self.categories = [
            "M&A",
            "Spin-offs",
            "Buybacks",
            "Guidance",
            "Leadership",
            "Approvals",
            "Activism",
            "Earnings",
            "Offerings",
            "Partnerships",
            "Litigation",
            "Restructuring",
            "Contracts",
            "Clinical Trials",
            "General",
        ]

        self.category_descriptions = {
            "M&A": "mergers, acquisitions, divestitures, takeover bids, purchases, buying companies",
            "Spin-offs": "spin-offs, carve-outs, separating business units, splitting companies",
            "Buybacks": "share buybacks, stock repurchases, special dividends, capital returns to shareholders",
            "Guidance": "earnings guidance, financial forecasts, outlook revisions, pre-announcements, preliminary results",
            "Leadership": "CEO/CFO appointments, executive departures, board member changes, management transitions",
            "Approvals": "FDA approvals, regulatory clearances, product approvals, licenses granted",
            "Activism": "activist investors, shareholder activism, proxy fights, corporate governance demands",
            "Earnings": "quarterly or annual earnings releases, revenue reports, financial results",
            "Offerings": "IPOs, secondary offerings, debt issuances, convertible notes, equity raises",
            "Partnerships": "strategic alliances, joint ventures, licensing deals, distribution agreements",
            "Litigation": "lawsuits, settlements, regulatory investigations, SEC enforcement actions",
            "Restructuring": "layoffs, cost-cutting, reorganizations, plant closures, bankruptcy filings",
            "Contracts": "major contract wins, government awards, large customer deals",
            "Clinical Trials": "clinical trial results, pipeline updates, study data (biotech/pharma)",
            "General": "material events that do not fit any of the above categories",
        }

        self.logger.info("ArticleTransformer ready with 15 categories")

    def _preprocess_text(self, text: str) -> str:
        """Clean and truncate text for optimal processing."""
        if not text or not isinstance(text, str):
            return ""

        text = ' '.join(text.split())

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
4. CATEGORY - pick the SINGLE most relevant category from the list below
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

    def _validate_category(self, category: str) -> str:
        """Ensure returned category is valid."""
        if category in self.categories:
            return category

        # Check aliases
        category_lower = category.lower().strip()
        if category_lower in CATEGORY_ALIASES:
            return CATEGORY_ALIASES[category_lower]

        # Case-insensitive match
        for valid_cat in self.categories:
            if valid_cat.lower() == category_lower:
                return valid_cat

        self.logger.warning(f"Unknown category '{category}', defaulting to 'General'")
        return "General"

    def _parse_response(self, output: str, threshold: float, original_title: str) -> Tuple[str, List[str], str, str]:
        """Parse API response and extract title, bullets, summary, category."""
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', output).strip()

            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}')
            if json_start != -1 and json_end > json_start:
                cleaned = cleaned[json_start:json_end + 1]

            parsed = json.loads(cleaned)

            title = parsed.get('title', original_title)[:100]
            bullets = parsed.get('bullets', [])
            summary = parsed.get('summary', 'No summary available')[:1000]
            category = self._validate_category(parsed.get('category', 'General'))
            confidence = float(parsed.get('confidence', 0.5))

            if confidence < threshold and category != "General":
                self.logger.info(f"Confidence {confidence} below threshold {threshold}, using 'General'")
                category = "General"

            return title, bullets, summary, category

        except json.JSONDecodeError:
            self.logger.warning(f"JSON parsing failed, trying regex extraction. Raw output (first 500 chars): {output[:500]}")

            try:
                title_match = re.search(r'"title"\s*:\s*"((?:[^"\\]|\\.)*)"', output)
                bullets_match = re.search(r'"bullets"\s*:\s*\[([^\]]+)\]', output)
                summary_match = re.search(r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"', output)
                category_match = re.search(r'"category"\s*:\s*"((?:[^"\\]|\\.)*)"', output)

                if all([title_match, summary_match, category_match]):
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
            cleaned_text = self._preprocess_text(article_text)
            cleaned_title = self._preprocess_text(title)

            prompt = self._build_prompt(cleaned_title, cleaned_text, threshold)

            raw_output, _model = self.groq_pool.call(
                prompt,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            result_title, bullets, summary, category = self._parse_response(raw_output, threshold, cleaned_title)

            self.logger.info(f"Transformed: {category}")
            return result_title, bullets, summary, category

        except Exception as e:
            self.logger.error(f"Transformation failed: {e}")
            return title, [], f"Error generating summary: {str(e)}", "General"
