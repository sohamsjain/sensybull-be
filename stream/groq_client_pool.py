"""
Shared Groq API client pool with model rotation for rate limit handling.

Both MaterialityFilter and ArticleTransformer share a single pool instance
so rate-limit rotation state is coordinated across all LLM calls.
"""
from groq import Groq
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass
import logging
import os
import time


@dataclass
class GroqClientPoolConfig:
    """Configuration for the shared Groq client pool."""
    models: List[str] = None
    temperature: float = 0.1
    max_tokens: int = 1024
    enable_model_rotation: bool = True

    def __post_init__(self):
        if self.models is None:
            self.models = [
                # Tier 1: High volume, fast (14.4K RPD)
                "llama-3.1-8b-instant",

                # Tier 2: Newer Llama 4 models (likely 1K RPD)
                "meta-llama/llama-4-maverick-17b-128e-instruct",

                # Tier 3: High quality (1K RPD)
                "llama-3.3-70b-versatile",

                # Tier 4: Unlimited tokens fallback (250 RPD)
                "groq/compound",
                "groq/compound-mini",

                # Tier 5: Additional alternatives
                "allam-2-7b",
                "moonshotai/kimi-k2-instruct",
                "openai/gpt-oss-20b"
            ]


class GroqClientPool:
    """
    Shared Groq API client with automatic model rotation on rate limits.

    Create one instance and inject it into both MaterialityFilter and
    ArticleTransformer so they share rotation state.
    """

    def __init__(self, api_key: str = None, config: GroqClientPoolConfig = None):
        if api_key is None:
            api_key = os.environ.get('GROQ_API_KEY')

        if not api_key:
            raise ValueError(
                "API key is required. Provide it as parameter or set GROQ_API_KEY environment variable."
            )

        self.logger = logging.getLogger(__name__)
        self.config = config or GroqClientPoolConfig()
        self.client = Groq(api_key=api_key)

        # Model rotation state
        self.current_model_index = 0
        self.model_failures = {model: 0 for model in self.config.models}
        self.model_last_used = {model: 0 for model in self.config.models}
        self.total_api_calls = 0
        self.successful_calls_by_model = {model: 0 for model in self.config.models}

        self.logger.info(f"GroqClientPool initialized with {len(self.config.models)} models")
        self.logger.info(f"Model rotation: {self.config.enable_model_rotation}")
        self.logger.info(f"Available models: {', '.join(self.config.models)}")

    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if an error is a rate limit error."""
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
        """Get the next model in rotation."""
        if not self.config.enable_model_rotation:
            return self.config.models[0]

        self.current_model_index = (self.current_model_index + 1) % len(self.config.models)
        next_model = self.config.models[self.current_model_index]

        self.logger.info(f"Switching to model: {next_model}")
        return next_model

    def call(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, str]:
        """
        Call Groq API with model rotation on rate limits.

        Args:
            prompt: The prompt to send
            temperature: Override default temperature (optional)
            max_tokens: Override default max_tokens (optional)

        Returns:
            Tuple of (response_text, model_used)
        """
        temp = temperature if temperature is not None else self.config.temperature
        tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        models_tried = set()
        last_error = None

        while len(models_tried) < len(self.config.models):
            current_model = self.config.models[self.current_model_index]

            if current_model in models_tried:
                break

            models_tried.add(current_model)

            try:
                self.logger.info(f"Attempting API call with model: {current_model}")

                response = self.client.chat.completions.create(
                    model=current_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    max_tokens=tokens,
                )

                self.total_api_calls += 1
                self.successful_calls_by_model[current_model] += 1
                self.model_last_used[current_model] = time.time()

                self.logger.info(
                    f"Success with {current_model} "
                    f"(Total calls: {self.successful_calls_by_model[current_model]})"
                )

                return response.choices[0].message.content.strip(), current_model

            except Exception as e:
                last_error = e
                self.model_failures[current_model] += 1

                if self._is_rate_limit_error(e):
                    self.logger.warning(
                        f"Rate limit hit for {current_model}: {str(e)[:100]}"
                    )
                    if (
                        self.config.enable_model_rotation
                        and len(models_tried) < len(self.config.models)
                    ):
                        self.logger.info("Rotating to next model...")
                        self._get_next_model()
                        time.sleep(1)
                        continue
                    else:
                        self.logger.error("All models rate limited or rotation disabled")
                        raise
                else:
                    self.logger.error(f"API call failed with {current_model}: {e}")
                    raise

        self.logger.error(f"All {len(self.config.models)} models failed or rate limited")
        raise last_error if last_error else Exception("All models unavailable")

    def get_stats(self) -> Dict:
        """Get usage statistics including model rotation info."""
        return {
            'total_api_calls': self.total_api_calls,
            'current_model': self.config.models[self.current_model_index],
            'successful_calls_by_model': self.successful_calls_by_model,
            'model_failures': self.model_failures,
            'model_rotation_enabled': self.config.enable_model_rotation,
            'available_models': self.config.models
        }

    def reset_stats(self):
        """Reset all usage statistics."""
        self.total_api_calls = 0
        self.successful_calls_by_model = {model: 0 for model in self.config.models}
        self.model_failures = {model: 0 for model in self.config.models}
        self.model_last_used = {model: 0 for model in self.config.models}
        self.logger.info("Statistics reset")
