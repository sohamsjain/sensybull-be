"""
RSS-based press release scraper

Polls RSS feeds from press release providers, fetches full articles,
runs them through AI transformation, and saves to the DB via API POST.
"""
import logging
import time
from datetime import datetime
from typing import Set

from ..http_client import HTTPClient
from ..article_transformer import ArticleTransformer
from ..storage_service import StorageService
from .feed_reader import FeedReader
from .pr_newswire_parser import PRNewswireParser
from .config import RSSConfig


class RSSScraper:
    """Main orchestrator for RSS-based press release scraping"""

    def __init__(self, config: RSSConfig = None):
        self.config = config or RSSConfig()

        # Setup logging
        logging.basicConfig(
            level=self.config.LOG_LEVEL,
            format=self.config.LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)

        # Shared infrastructure (same as Yahoo pipeline)
        self.http_client = HTTPClient(self.config.HEADERS)
        self.transformer = ArticleTransformer()
        self.storage = StorageService(self.http_client, self.config.API_ENDPOINT)

        # PR Newswire feed
        self.pr_newswire_reader = FeedReader(
            self.config.PR_NEWSWIRE_FEED_URL,
            self.config.HEADERS
        )
        self.pr_newswire_parser = PRNewswireParser()

        # Dedup across polls
        self.processed_urls: Set[str] = set()

    def scrape_continuously(self, poll_interval: int = None):
        """
        Continuously poll RSS feeds and process new press releases.

        Args:
            poll_interval: Override seconds between polls (uses config default if None)
        """
        poll_interval = poll_interval or self.config.POLL_INTERVAL
        self.logger.info("Starting RSS press release scraper...")

        while True:
            try:
                self._poll_pr_newswire()
            except Exception as e:
                self.logger.error(f"Error in RSS scrape cycle: {e}")

            self.logger.info(f"Waiting {poll_interval}s before next poll...")
            time.sleep(poll_interval)

    def _poll_pr_newswire(self):
        """Poll PR Newswire RSS feed and process new items"""
        items = self.pr_newswire_reader.fetch_new_items()
        articles_processed = 0

        for item in items:
            url = item['link']
            if url in self.processed_urls:
                continue

            self.logger.info(f"Processing: {item['title']}")
            self.logger.info(f"URL: {url}")

            # Fetch full press release page
            html = self.http_client.get(url)
            if not html:
                self.logger.warning(f"Failed to fetch article page: {url}")
                continue

            # Extract structured data from the page
            article_data = self.pr_newswire_parser.parse_article(url, html, item)
            if not article_data:
                continue

            # Run AI transformation (classification + summarization)
            try:
                title, bullets, summary, topic = self.transformer.transform(
                    article_data['title'],
                    article_data['article_text']
                )
                article_data['title'] = title
                article_data['bullets'] = bullets
                article_data['summary'] = summary
                article_data['topics'] = [topic]
            except Exception as e:
                self.logger.error(f"Transformer failed for {url}: {e}")
                text = article_data['article_text']
                article_data['bullets'] = []
                article_data['summary'] = text[:500] + "..." if len(text) > 500 else text
                article_data['topics'] = ['General']

            article_data['extracted_at'] = datetime.now().isoformat()

            # Save to DB via API POST
            if self.storage.save_article(article_data):
                self.processed_urls.add(url)
                articles_processed += 1

            time.sleep(self.config.ARTICLE_PROCESSING_DELAY)

        if articles_processed:
            self.logger.info(f"Processed {articles_processed} new PR Newswire articles")
