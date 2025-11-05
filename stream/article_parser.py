"""
Parser for individual Yahoo Finance articles
"""
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re
import logging
from html import unescape
from typing import Optional, Dict, List
from .article_transformer import ArticleTransformer


class ArticleParser:
    """Parses individual Yahoo Finance article pages"""

    # List of permissible providers
    EXTENDED_PERMISSIBLE_PROVIDERS = [
        "GlobeNewswire",
        "ACCESS Newswire",
        "PR Newswire",
        "Business Wire",
        "Newsfile",
        "NewMediaWire",
        "Reuters",
        "Bloomberg",
        "TheStreet",
        "MarketWatch",
        "Seeking Alpha",
        "Benzinga",
        "Barron's",
        "The Wall Street Journal",
        "Financial Times"
    ]

    PERMISSIBLE_PROVIDERS = [
        "GlobeNewswire",
        "ACCESS Newswire",
        "PR Newswire",
        "Business Wire",
        "Newsfile",
    ]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.article_transformer = ArticleTransformer()

    def extract_article_data(self, article_url: str, html_content: str) -> Optional[Dict]:
        """
        Extract structured data from an article page

        Args:
            article_url: The article URL
            html_content: Raw HTML content

        Returns:
            Dictionary with article data, or None if extraction fails
        """
        if not html_content:
            self.logger.error(f"No HTML content provided for {article_url}")
            return None

        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Find script tag with article data
            script_element = self._find_article_script(soup, article_url)
            if not script_element:
                return None

            # Parse JSON data
            article_json = self._parse_article_json(script_element)
            if not article_json:
                return None

            # Extract all required fields
            return self._extract_fields(article_url, article_json)

        except Exception as e:
            self.logger.error(f"Unexpected error extracting article data from {article_url}: {e}")
            return None

    def _find_article_script(self, soup: BeautifulSoup, article_url: str) -> Optional[any]:
        """Find the script tag containing article data"""
        url_path = article_url.split("/news/")[1] if "/news/" in article_url else ""
        pattern = re.compile(url_path)

        def has_data_url(tag):
            if 'data-url' in tag.attrs and isinstance(tag['data-url'], str):
                return pattern.search(tag['data-url'])
            return False

        matching_elements = soup.find_all(has_data_url)
        if not matching_elements:
            self.logger.error(f"Could not find article data script for {article_url}")
            return None

        return matching_elements[0]

    def _parse_article_json(self, script_element) -> Optional[Dict]:
        """Parse nested JSON structure from script element"""
        try:
            data = json.loads(script_element.contents[0])
            data = json.loads(data.get('body', '{}'))

            items = data.get('items', [])
            if not items:
                self.logger.error("No items found in article data")
                return None

            return items[0].get('data', {})
        except (json.JSONDecodeError, IndexError, KeyError) as e:
            self.logger.error(f"Error parsing article JSON: {e}")
            return None

    def _extract_fields(self, article_url: str, article_data: Dict) -> Optional[Dict]:
        """Extract all required fields from article data"""
        content_meta = article_data.get('contentMeta', {})

        # Extract provider info
        provider, provider_url = self._extract_provider(content_meta)
        if not provider or not provider_url:
            self.logger.error(f"No provider information found for {article_url}")
            return None

        # FILTER: Check if provider is in the permissible list
        if provider not in self.PERMISSIBLE_PROVIDERS:
            self.logger.info(f"Discarding article from non-permissible provider '{provider}': {article_url}")
            return None

        # Extract tickers
        tickers = self._extract_tickers(content_meta)

        # FILTER: Check if article has at least one ticker
        if not tickers or len(tickers) == 0:
            self.logger.info(f"Discarding article with no tickers: {article_url}")
            return None

        # Extract timestamp
        timestamp = self._extract_timestamp(content_meta)
        if not timestamp:
            self.logger.error(f"No timestamp found for {article_url}")
            return None

        # Extract title
        title = self._extract_title(content_meta)
        if not title:
            self.logger.error(f"No title found for {article_url}")
            return None

        # Extract image
        image_url = self._extract_image(content_meta)

        # Extract article text
        article_text = self._extract_article_text(content_meta)

        # Classification & Summarization using ArticleTransformer
        try:
            refined_title, bullets, summary, topic = self.article_transformer.transform(title, article_text)
            self.logger.info(f"Article classified as '{topic}': {article_url}")
        except Exception as e:
            self.logger.error(f"Transformer failed for {article_url}: {e}")
            # Use fallback values if transformation fails
            refined_title = title
            bullets = []
            summary = article_text[:500] + "..." if len(article_text) > 500 else article_text
            topic = "General"

        return {
            'url': article_url,
            'title': refined_title,  # Using refined title from transformer
            'timestamp': timestamp,
            'provider': provider,
            'provider_url': provider_url,
            'bullets': bullets,  # Bullet points from transformer
            'summary': summary,  # Summary from transformer
            'topics': [topic],  # Category from transformer
            'image_url': image_url,
            'tickers': tickers,
            'article_text': article_text,  # Keep original text
            'extracted_at': datetime.now().isoformat()
        }

    def _extract_timestamp(self, content_meta: Dict) -> Optional[int]:
        """Extract timestamp from content metadata"""
        dates = content_meta.get('dates', {})
        display_date = dates.get('displayDate', {})
        return display_date.get('timestamp')

    def _extract_title(self, content_meta: Dict) -> Optional[str]:
        """Extract title from content metadata"""
        seo_meta = content_meta.get('seoMeta', {})
        return seo_meta.get('title')

    def _extract_provider(self, content_meta: Dict) -> tuple[Optional[str], Optional[str]]:
        """Extract provider name and URL"""
        seo_meta = content_meta.get('seoMeta', {})
        provider_url = seo_meta.get('providerContentUrl')

        if provider_url:
            provider = content_meta.get('attribution', {}).get('provider', {}).get('name')
        else:
            provider_url = seo_meta.get('canonicalUrl')
            provider = "Yahoo Finance"

        return provider, provider_url

    def _extract_image(self, content_meta: Dict) -> Optional[str]:
        """Extract primary image URL"""
        content_images = content_meta.get('contentImages', {})
        primary_image = content_images.get('primaryImage', {})
        original_image = primary_image.get('original', {})
        return original_image.get('url')

    def _extract_tickers(self, content_meta: Dict) -> List[str]:
        """Extract stock tickers from content metadata"""
        tickers = []
        content_tags = content_meta.get('contentTags', {})
        stockTickers = content_tags.get('stockTickers', [])

        for item in stockTickers:
            tickers.append(item.get('symbol'))

        return tickers

    def _extract_article_text(self, content_meta: Dict) -> str:
        """Extract and clean article text from story atoms"""
        story_atoms = content_meta.get('storyAtoms', [])
        article_text = ''

        for atom in story_atoms:
            if atom.get('type') == 'text':
                content = atom.get('content', '')
                # Remove HTML tags and decode entities
                clean_content = re.sub(r'<[^>]+>', '', unescape(content))
                if clean_content:
                    article_text += clean_content + "\n\n"

        return article_text.strip()