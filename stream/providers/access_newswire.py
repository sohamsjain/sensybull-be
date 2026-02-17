"""
Access Newswire (formerly ACCESSWIRE) press release provider.

RSS Feed: https://www.accesswire.com/rssfeed.aspx
Fallback listing: https://www.accessnewswire.com/newsroom
Article text typically lives in <div class="release-body"> or <article>.

The company was formerly known as Issuer Direct Corporation and rebranded
to Access Newswire Inc. in January 2025. Domains include accessnewswire.com,
accesswire.com, newswire.com, and pressrelease.com.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import re
import time

from .base import BaseProvider


class AccessNewswireProvider(BaseProvider):

    PROVIDER = "ACCESS Newswire"
    FEED_URL = "https://www.accesswire.com/rssfeed.aspx"
    FEED_MODE = "rss"
    LISTING_URL = "https://www.accessnewswire.com/newsroom"
    POLL_INTERVAL = 90

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
            self.logger.error(f"Error parsing Access Newswire article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        # Access Newswire / ACCESSWIRE page structure
        body = soup.find('div', class_='release-body')

        if not body:
            body = soup.find('div', id='annotate-release')

        if not body:
            body = soup.find('div', class_='article-content')

        # Fallback: generic article tag
        if not body:
            body = soup.find('article')

        if body:
            for tag in body.find_all(['script', 'style', 'nav']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        return ''

    def get_listing_urls(self, html: str) -> List[Dict]:
        """Extract article links from Access Newswire newsroom page (scrape-mode fallback)."""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        for link in soup.find_all('a', href=True):
            href = link['href']
            # Access Newswire article URLs typically contain a numeric ID
            if '/newsroom/' in href or re.search(r'/\d{6,}', href):
                full_url = href if href.startswith('http') else f"https://www.accessnewswire.com{href}"
                title = link.get_text(strip=True)
                if title and full_url not in [item['link'] for item in items]:
                    items.append({
                        'title': title,
                        'link': full_url,
                        'published': int(time.time()) * 1000,
                        'guid': full_url,
                    })

        self.logger.info(f"Found {len(items)} articles on Access Newswire newsroom page")
        return items
