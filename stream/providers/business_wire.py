"""
Business Wire press release provider.

RSS Feed: https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeEFpRWg==
Article text lives in <div class="bw-release-story"> or <div class="bwNewRelease">.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict

from .base import BaseProvider


class BusinessWireProvider(BaseProvider):

    PROVIDER = "Business Wire"
    FEED_URL = "https://feed.businesswire.com/rss/home/?rss=G1QFDERJXkJeEFpRWg=="
    FEED_MODE = "rss"
    POLL_INTERVAL = 60

    def parse_article(self, url: str, html_content: str, feed_item: dict) -> Optional[Dict]:
        if not html_content:
            self.logger.error(f"No HTML content for {url}")
            return None

        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            article_text = self._extract_article_text(soup)
            if not article_text:
                self.logger.warning(f"No article text extracted from {url}")
                return None

            tickers = self._extract_tickers(article_text)
            image_url = self._extract_image(soup)
            return self._build_article_dict(url, feed_item, article_text, tickers, image_url)

        except Exception as e:
            self.logger.error(f"Error parsing Business Wire article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        # Business Wire primary container
        body = soup.find('div', class_='bw-release-story')

        # Fallback: older Business Wire format
        if not body:
            body = soup.find('div', class_='bwNewRelease')

        # Fallback: role-based selector
        if not body:
            body = soup.find('div', attrs={'role': 'article'})

        # Fallback: generic article tag
        if not body:
            body = soup.find('article')

        if body:
            for tag in body.find_all(['script', 'style', 'nav']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        return ''
