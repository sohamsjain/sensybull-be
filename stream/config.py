"""
Central configuration for the press release pipeline.
"""


class PipelineConfig:
    """Unified configuration for the multi-provider press release pipeline."""

    # API endpoint for storing articles
    API_ENDPOINT = "http://localhost:5000/articles"

    # HTTP headers for scraping
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Delay between processing individual articles (seconds)
    ARTICLE_PROCESSING_DELAY = 1

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
