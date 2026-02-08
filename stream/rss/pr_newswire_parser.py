"""
Parser for PR Newswire press release pages
"""
from bs4 import BeautifulSoup
import re
import logging
from typing import Optional, Dict, List


class PRNewswireParser:
    """Extracts structured article data from PR Newswire press release pages"""

    PROVIDER = "PR Newswire"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_article(self, url: str, html_content: str, feed_item: dict) -> Optional[Dict]:
        """
        Parse a PR Newswire article page and combine with RSS feed metadata.

        Args:
            url: The press release URL
            html_content: Raw HTML of the page
            feed_item: Dict from FeedReader with title, published, etc.

        Returns:
            Article dict ready for transformation, or None on failure
        """
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

        except Exception as e:
            self.logger.error(f"Error parsing PR Newswire article {url}: {e}")
            return None

    def _extract_article_text(self, soup: BeautifulSoup) -> str:
        """Extract the press release body text"""
        # PR Newswire wraps the release in a section.release-body container
        body = soup.find('section', class_='release-body')
        if not body:
            body = soup.find('div', class_='release-body')

        if body:
            for tag in body.find_all(['script', 'style']):
                tag.decompose()
            return body.get_text(separator='\n', strip=True)

        # Fallback: look for the article tag
        article = soup.find('article')
        if article:
            for tag in article.find_all(['script', 'style']):
                tag.decompose()
            return article.get_text(separator='\n', strip=True)

        return ''

    def _extract_tickers(self, text: str) -> List[str]:
        """Extract stock ticker symbols from cashtag patterns ($AAPL) in the text"""
        tickers = re.findall(r'\$([A-Z]{1,5})\b', text)
        return list(set(tickers))

    def _extract_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract a featured image URL from the page"""
        # Prefer Open Graph image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']

        # Fall back to first image inside the release body
        body = soup.find('section', class_='release-body') or \
               soup.find('div', class_='release-body')
        if body:
            img = body.find('img')
            if img and img.get('src'):
                return img['src']

        return None
