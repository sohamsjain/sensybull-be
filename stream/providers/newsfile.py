"""
Newsfile Corp press release provider.

Newsfile provides category-based RSS feeds and a listing page.
Primary scrape target: https://www.newsfilecorp.com/newscategories.php
Article text typically lives in <div class="article-content"> or <div id="release-body">.

This provider supports both RSS mode (if a feed URL is available) and
scrape mode as a fallback.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import re
import time

from .base import BaseProvider


class NewsfileProvider(BaseProvider):

    PROVIDER = "Newsfile"
    FEED_URL = "https://www.newsfilecorp.com/rss"
    FEED_MODE = "rss"
    LISTING_URL = "https://www.newsfilecorp.com/newscategories.php"
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
            self.logger.error(f"Error parsing Newsfile article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        # Newsfile uses article-content or release-body
        body = soup.find('div', class_='article-content')

        if not body:
            body = soup.find('div', id='release-body')

        if not body:
            body = soup.find('div', class_='news-content')

        # Fallback: generic article tag
        if not body:
            body = soup.find('article')

        if body:
            for tag in body.find_all(['script', 'style', 'nav']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        return ''

    def get_listing_urls(self, html: str) -> List[Dict]:
        """Extract article links from Newsfile's listing page (scrape-mode fallback)."""
        soup = BeautifulSoup(html, 'html.parser')
        items = []

        # Newsfile listing page has links to individual press releases
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Newsfile article URLs typically contain a numeric ID
            if '/release/' in href or re.search(r'/\d+/', href):
                full_url = href if href.startswith('http') else f"https://www.newsfilecorp.com{href}"
                title = link.get_text(strip=True)
                if title and full_url not in [item['link'] for item in items]:
                    items.append({
                        'title': title,
                        'link': full_url,
                        'published': int(time.time()) * 1000,
                        'guid': full_url,
                    })

        self.logger.info(f"Found {len(items)} articles on Newsfile listing page")
        return items
