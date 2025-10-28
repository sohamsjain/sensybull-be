"""
Configuration settings for Article Streamer
"""
import os
from datetime import datetime, UTC


class Config:
    """Central configuration for the scraper"""

    # URLs
    BASE_URL = "https://finance.yahoo.com/sitemap"
    API_ENDPOINT = "http://localhost:5000/articles"

    # Headers
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # File paths
    OUTPUT_FILE = "yahoo_finance_articles.json"

    # Timing
    SCRAPE_INTERVAL = 10  # seconds between scrape cycles
    PAGE_RETRY_INTERVAL = 60  # seconds before retrying last page
    ARTICLE_PROCESSING_DELAY = 1  # seconds between articles
    PAGE_TRANSITION_DELAY = 2  # seconds between pages

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    @staticmethod
    def get_today_date_string():
        """Get today's date in Yahoo Finance sitemap format"""
        return datetime.now(UTC).strftime("%Y_%m_%d")

    @staticmethod
    def get_initial_url():
        """Generate the initial URL for today's sitemap"""
        date_str = Config.get_today_date_string()
        return f"{Config.BASE_URL}/{date_str}_start"