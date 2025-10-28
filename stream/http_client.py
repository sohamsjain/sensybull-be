"""
HTTP client for making requests
"""
import requests
import logging
from typing import Optional


class HTTPClient:
    """Handles all HTTP requests"""

    def __init__(self, headers: dict):
        self.headers = headers
        self.logger = logging.getLogger(__name__)

    def get(self, url: str) -> Optional[str]:
        """
        Fetch content from a URL

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if request fails
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            return None

    def post(self, url: str, data: dict) -> tuple[bool, int]:
        """
        Post JSON data to a URL

        Args:
            url: The API endpoint
            data: Dictionary to send as JSON

        Returns:
            Tuple of (success: bool, status_code: int)
        """
        try:
            import json
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(data)
            )
            return (response.status_code == 201, response.status_code)
        except requests.RequestException as e:
            self.logger.error(f"Error posting to {url}: {e}")
            return (False, 0)