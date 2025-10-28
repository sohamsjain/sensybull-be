"""
Article processing orchestration
"""
import logging
from typing import Set
from .http_client import HTTPClient
from .article_parser import ArticleParser
from .storage_service import StorageService


class ArticleProcessor:
    """Orchestrates article extraction and storage"""

    def __init__(
            self,
            http_client: HTTPClient,
            article_parser: ArticleParser,
            storage_service: StorageService
    ):
        self.http_client = http_client
        self.article_parser = article_parser
        self.storage_service = storage_service
        self.processed_articles: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    def process_article(self, article_url: str) -> bool:
        """
        Process a single article: fetch, parse, and store

        Args:
            article_url: The URL of the article to process

        Returns:
            True if successfully processed, False otherwise
        """
        if article_url in self.processed_articles:
            self.logger.info(f"Skipping already processed article: {article_url}")
            return False

        self.logger.info(f"Processing article: {article_url}")

        # Fetch article HTML
        html_content = self.http_client.get(article_url)
        if not html_content:
            self.logger.error(f"Failed to fetch article: {article_url}")
            return False

        # Parse article data
        article_data = self.article_parser.extract_article_data(article_url, html_content)
        if not article_data:
            self.logger.warning(f"Failed to extract valid data for article: {article_url}")
            return False

        # Save article
        if self.storage_service.save_article(article_data):
            self.processed_articles.add(article_url)
            return True

        return False