"""
Configuration settings for RSS feed readers
"""


class RSSConfig:
    """Central configuration for the RSS scraper"""

    # RSS Feed URLs
    PR_NEWSWIRE_FEED_URL = "https://www.prnewswire.com/rss/news-releases-list.rss"

    # API
    API_ENDPOINT = "http://localhost:5000/articles"

    # Headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Timing
    POLL_INTERVAL = 60  # seconds between feed polls
    ARTICLE_PROCESSING_DELAY = 1  # seconds between processing articles

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
