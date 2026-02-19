"""
PR Newswire press release provider.

RSS Feed: https://www.prnewswire.com/rss/news-releases-list.rss
Article text lives in <section class="release-body"> or <div class="release-body">.
"""
from bs4 import BeautifulSoup
from typing import Optional, Dict, List

from .base import BaseProvider


class PRNewswireProvider(BaseProvider):

    PROVIDER = "PR Newswire"
    FEED_URL = "https://www.prnewswire.com/rss/news-releases-list.rss"
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
            self.logger.error(f"Error parsing PR Newswire article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        body = soup.find('section', class_='release-body')
        if not body:
            body = soup.find('div', class_='release-body')

        if body:
            for tag in body.find_all(['script', 'style']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        article = soup.find('article')
        if article:
            for tag in article.find_all(['script', 'style']):
                tag.decompose()
            return article.get_text(separator='\n', strip=True)

        return ''

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        og = super()._extract_image(soup)
        if og:
            return og

        body = soup.find('section', class_='release-body') or \
               soup.find('div', class_='release-body')
        if body:
            img = body.find('img')
            if img and img.get('src'):
                return img['src']

        return None
