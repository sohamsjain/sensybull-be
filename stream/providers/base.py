"""
Abstract base class for press release provider parsers.

Each provider implements this interface so the Orchestrator can
poll, parse, transform, and store articles from any source uniformly.
"""
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import re
import logging


class BaseProvider(ABC):
    """
    Abstract base for all press release provider parsers.

    Subclasses MUST set class attributes:
        PROVIDER       - Human-readable name (e.g. "PR Newswire")
        FEED_URL       - RSS feed URL (empty string if scrape-mode)
        FEED_MODE      - "rss" or "scrape"
        POLL_INTERVAL  - Seconds between poll cycles

    Subclasses MUST implement:
        parse_article()
        _extract_article_text()

    Subclasses MAY override:
        _extract_tickers()
        _extract_image()
        get_listing_urls()   (required for scrape-mode providers)
    """

    PROVIDER: str = ""
    FEED_URL: str = ""
    FEED_MODE: str = "rss"        # "rss" or "scrape"
    LISTING_URL: str = ""         # only for scrape-mode providers
    POLL_INTERVAL: int = 60       # seconds between polls

    def __init__(self):
        self.logger = logging.getLogger(f"stream.providers.{self.PROVIDER}")

    @abstractmethod
    def parse_article(self, url: str, html_content: str, feed_item: dict) -> Optional[Dict]:
        """
        Parse a full press release page into a structured article dict.

        Args:
            url: The press release URL
            html_content: Raw HTML of the page
            feed_item: Dict from FeedReader (title, link, published, guid)

        Returns:
            Article dict with keys: url, title, timestamp, provider,
            provider_url, image_url, article_text, tickers.
            None if parsing fails or content is unusable.
        """
        pass

    @abstractmethod
    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        """Extract the press release body text from parsed HTML."""
        pass

    def _extract_tickers(self, text: str, soup: Optional[BeautifulSoup] = None) -> List[str]:
        """Extract stock ticker symbols from exchange-qualified patterns like (NYSE:AAPL) or (NASDAQ:TSLA).

        Only NYSE and NASDAQ tickers are returned. Articles with no such
        patterns are considered unrelated to a publicly-traded stock.
        """
        matches = re.findall(r'\((NYSE|NASDAQ):\s*([A-Z]{1,5})\)', text)
        return list({symbol for _exchange, symbol in matches})

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract a featured image URL, defaulting to og:image meta tag."""
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        return None

    def _build_article_dict(self, url: str, feed_item: dict,
                            article_text: str, tickers: List[str],
                            image_url: Optional[str]) -> Dict:
        """Assemble the standard article dict expected by StorageService."""
        return {
            'url': url,
            'title': feed_item.get('title', ''),
            'timestamp': feed_item.get('published'),
            'provider': self.PROVIDER,
            'provider_url': url,
            'image_url': image_url,
            'article_text': article_text,
            'tickers': tickers,
        }

    def get_listing_urls(self, html: str) -> List[Dict]:
        """
        For scrape-mode providers: extract article links from a listing page.

        Returns:
            List of dicts matching FeedReader output shape:
            [{'title': ..., 'link': ..., 'published': ..., 'guid': ...}, ...]
        """
        raise NotImplementedError(
            f"{self.PROVIDER} uses scrape mode but get_listing_urls() is not implemented"
        )
