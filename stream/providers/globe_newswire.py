"""
Globe Newswire press release provider.

RSS Feed: https://www.globenewswire.com/RssFeed/subjectcode/72-Press+Releases/feedTitle/GlobeNewswire+-+Press+Releases
Article text lives in <div class="main-body-container"> or the notified-body div.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict

from .base import BaseProvider


class GlobeNewswireProvider(BaseProvider):

    PROVIDER = "GlobeNewswire"
    FEED_URL = "https://www.globenewswire.com/RssFeed/subjectcode/72-Press+Releases/feedTitle/GlobeNewswire+-+Press+Releases"
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
            self.logger.error(f"Error parsing GlobeNewswire article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        # GlobeNewswire uses main-body-container for press release text
        body = soup.find('div', class_='main-body-container')

        # Fallback: notified-body (used in some regulatory filings)
        if not body:
            body = soup.find('div', class_='notified-body')

        # Fallback: article-body
        if not body:
            body = soup.find('div', class_='article-body')

        # Fallback: generic article tag
        if not body:
            body = soup.find('article')

        if body:
            for tag in body.find_all(['script', 'style', 'nav']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        return ''
