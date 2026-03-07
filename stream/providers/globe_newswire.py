"""
Globe Newswire press release provider.

RSS Feed: https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies
Tickers are extracted from RSS <category> elements with domain="/rss/stock",
e.g. <category domain="https://www.globenewswire.com/rss/stock">NYSE:HGTY</category>
Only NYSE and Nasdaq listed tickers are kept.
Article text lives in <div class="main-body-container"> or the notified-body div.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict, List

from .base import BaseProvider

ALLOWED_EXCHANGES = {'NYSE', 'NASDAQ'}


class GlobeNewswireProvider(BaseProvider):

    PROVIDER = "GlobeNewswire"
    FEED_URL = "https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/GlobeNewswire%20-%20News%20about%20Public%20Companies"
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

            tickers = self._extract_tickers_from_feed(feed_item)
            image_url = self._extract_image(soup)
            return self._build_article_dict(url, feed_item, article_text, tickers, image_url)

        except Exception as e:
            self.logger.error(f"Error parsing GlobeNewswire article {url}: {e}")
            return None

    def _extract_tickers_from_feed(self, feed_item: dict) -> List[str]:
        """Extract NYSE/Nasdaq tickers from RSS category tags.

        feedparser exposes <category> elements as entry.tags, where each tag
        is a dict with keys: term, scheme, label.
        """
        tickers = set()
        for tag in feed_item.get('tags', []):
            scheme = tag.get('scheme', '') or ''
            if '/rss/stock' not in scheme:
                continue
            term = tag.get('term', '')
            if ':' not in term:
                continue
            exchange, symbol = term.split(':', 1)
            if exchange.strip().upper() in ALLOWED_EXCHANGES and symbol.strip():
                tickers.add(symbol.strip().upper())
        return list(tickers)

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
