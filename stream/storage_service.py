"""
Storage service for persisting articles
"""
import logging
from typing import Dict
from .http_client import HTTPClient


class StorageService:
    """Handles article storage operations"""

    def __init__(self, http_client: HTTPClient, api_endpoint: str):
        self.http_client = http_client
        self.api_endpoint = api_endpoint
        self.logger = logging.getLogger(__name__)

    def save_article(self, article: Dict) -> bool:
        """
        Save an article to the API

        Args:
            article: Dictionary containing article data

        Returns:
            True if successful, False otherwise
        """
        try:
            success, status_code = self.http_client.post(self.api_endpoint, article)

            if success:
                self.logger.info(f"Article stored successfully: {article['url']}")
                return True
            else:
                self.logger.warning(f"Failed to store article (status {status_code}): {article['url']}")
                return False

        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False