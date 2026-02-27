"""
LLM-based materiality filter for press releases.

Assesses whether a press release describes a material event that could
impact a company's stock price or business fundamentals. Runs as a
lightweight gate before the heavier ArticleTransformer.
"""
from dataclasses import dataclass
from typing import Optional
import json
import re
import logging

from .groq_client_pool import GroqClientPool


@dataclass
class MaterialityConfig:
    """Configuration for materiality filtering."""
    material_threshold: float = 0.6
    borderline_threshold: float = 0.4
    max_text_length: int = 500
    temperature: float = 0.05
    max_tokens: int = 256


@dataclass
class MaterialityResult:
    """Result of a materiality assessment."""
    is_material: bool
    score: float
    reason: str
    is_borderline: bool


class MaterialityFilter:
    """LLM-based materiality filter for press releases."""

    def __init__(self, groq_pool: GroqClientPool, config: MaterialityConfig = None):
        self.groq_pool = groq_pool
        self.config = config or MaterialityConfig()
        self.logger = logging.getLogger(__name__)

    def assess(self, title: str, article_text: str) -> MaterialityResult:
        """
        Assess whether a press release describes a material event.

        Args:
            title: The article title
            article_text: The full article text

        Returns:
            MaterialityResult with score, is_material flag, and reasoning
        """
        truncated_text = ""
        if article_text:
            truncated_text = ' '.join(article_text.split())[:self.config.max_text_length]

        prompt = self._build_prompt(title, truncated_text)

        raw_output, _ = self.groq_pool.call(
            prompt,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return self._parse_response(raw_output)

    def _build_prompt(self, title: str, text: str) -> str:
        return f"""You are a financial materiality analyst. Assess whether this press release describes a MATERIAL event that could meaningfully impact a company's stock price or business fundamentals.

MATERIAL events include: earnings results, revenue guidance changes, M&A activity, executive changes, FDA approvals/rejections, activist campaigns, significant contract wins/losses, restructuring, lawsuits, offerings, clinical trial results, regulatory actions, spin-offs, buybacks, dividend changes.

IMMATERIAL events include: marketing campaigns, conference attendance, product webinars, CSR/sustainability reports, routine hiring announcements, award wins, minor partnerships, holiday greetings, routine product updates without financial impact.

PRESS RELEASE TITLE: {title}

PRESS RELEASE TEXT (excerpt):
{text}

Respond ONLY with valid JSON:
{{
  "materiality_score": 0.85,
  "is_material": true,
  "reason": "Brief one-sentence explanation"
}}"""

    def _parse_response(self, output: str) -> MaterialityResult:
        """Parse the LLM materiality response."""
        try:
            cleaned = re.sub(r'```json\s*|\s*```', '', output).strip()
            json_start = cleaned.find('{')
            json_end = cleaned.rfind('}')
            if json_start != -1 and json_end > json_start:
                cleaned = cleaned[json_start:json_end + 1]

            parsed = json.loads(cleaned)
            score = float(parsed.get('materiality_score', 0.5))
            score = max(0.0, min(1.0, score))

            is_material = score >= self.config.material_threshold
            is_borderline = (
                not is_material and score >= self.config.borderline_threshold
            )

            return MaterialityResult(
                is_material=is_material,
                score=score,
                reason=parsed.get('reason', 'No reason provided'),
                is_borderline=is_borderline,
            )
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            self.logger.warning(
                f"Failed to parse materiality response: {e}. Defaulting to material."
            )
            # Fail-open: treat as material to avoid data loss
            return MaterialityResult(
                is_material=True,
                score=0.5,
                reason="Parse failure - defaulting to material",
                is_borderline=False,
            )
