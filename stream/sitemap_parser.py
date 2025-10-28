"""
Parser for Yahoo Finance sitemap pages
"""
from bs4 import BeautifulSoup
from datetime import datetime
import re
import logging
from typing import Optional, List, Dict


class SitemapParser:
    """Parses Yahoo Finance sitemap pages"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.seen_articles = set()

    def extract_article_links(self, html_content: str) -> List[Dict[str, str]]:
        """
        Extract article links from sitemap HTML

        Args:
            html_content: Raw HTML content

        Returns:
            List of article dictionaries with url, title, and timestamp
        """
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []

        for link in soup.find_all('a', href=True):
            href = link['href']

            # Only include news article links, exclude navigation
            if '/news/' in href and href not in self.seen_articles:
                # Ensure absolute URL
                if not href.startswith('http'):
                    if href.startswith('/'):
                        href = f"https://finance.yahoo.com{href}"
                    else:
                        href = f"https://finance.yahoo.com/{href}"

                self.seen_articles.add(href)
                articles.append({
                    'url': href,
                    'title': link.text.strip(),
                    'timestamp': datetime.now().isoformat()
                })

        return articles

    def extract_next_page_token(self, html_content: str) -> Optional[str]:
        """
        Extract the next page token from pagination link

        Args:
            html_content: Raw HTML content

        Returns:
            Next page token string, or None if no next page
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            next_link = soup.find('a', string='Next')

            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                match = re.search(r'start(\d+)$', next_url)
                if match:
                    return match.group(1)
        except Exception as e:
            self.logger.error(f"Error extracting next page token: {e}")

        return None