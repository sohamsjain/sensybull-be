"""
Main scraper orchestration
"""
import logging
import time
from typing import Optional
from config import Config
from .http_client import HTTPClient
from .sitemap_parser import SitemapParser
from .article_parser import ArticleParser
from .storage_service import StorageService
from .article_processor import ArticleProcessor


class Scraper:
    """Main orchestrator for scraping operations"""

    def __init__(self, config: Config = None):
        self.config = config or Config()

        # Setup logging
        logging.basicConfig(
            level=self.config.LOG_LEVEL,
            format=self.config.LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.http_client = HTTPClient(self.config.HEADERS)
        self.sitemap_parser = SitemapParser()
        self.article_parser = ArticleParser()
        self.storage_service = StorageService(
            self.http_client,
            self.config.API_ENDPOINT
        )
        self.article_processor = ArticleProcessor(
            self.http_client,
            self.article_parser,
            self.storage_service
        )

    def scrape_continuously(
            self,
            interval: Optional[int] = None,
            page_retry_interval: Optional[int] = None
    ):
        """
        Continuously scrape sitemap pages

        Args:
            interval: Seconds between scrape cycles (uses config default if None)
            page_retry_interval: Seconds before retrying last page (uses config default if None)
        """
        interval = interval or self.config.SCRAPE_INTERVAL
        page_retry_interval = page_retry_interval or self.config.PAGE_RETRY_INTERVAL

        current_date = self.config.get_today_date_string()

        while True:
            try:
                current_url = f"{self.config.BASE_URL}/{current_date}/"
                print(f"Starting scrape cycle with URL: {current_url}")

                page_without_next = None

                while current_url:
                    # Fetch sitemap page
                    html_content = self.http_client.get(current_url)
                    if not html_content:
                        print("Failed to fetch page content.")
                        time.sleep(interval)
                        break

                    # Extract article links
                    articles = self.sitemap_parser.extract_article_links(html_content)

                    # Process articles
                    if articles:
                        self._process_articles(articles)

                    # Get next page token
                    next_token = self.sitemap_parser.extract_next_page_token(html_content)

                    if next_token:
                        # Move to next page
                        current_url = f"{self.config.BASE_URL}/{current_date}_start{next_token}"
                        print(f"Moving to next page: {current_url}")
                        page_without_next = None
                        time.sleep(self.config.PAGE_TRANSITION_DELAY)
                    else:
                        # No next page - check if date changed
                        new_date = self.config.get_today_date_string()
                        if new_date != current_date:
                            print(f"Date changed from {current_date} to {new_date}. Starting fresh cycle.")
                            current_date = new_date
                            break

                        # Reached last page for current date
                        if page_without_next != current_url:
                            page_without_next = current_url
                            print(f"Reached last available page. Will retry in {page_retry_interval} seconds.")

                        time.sleep(page_retry_interval)
                        print(f"Retrying last page: {current_url}")

                print(f"Completed cycle. Waiting {interval} seconds before checking again...")
                time.sleep(interval)

            except Exception as e:
                self.logger.error(f"Error in scrape cycle: {e}")
                time.sleep(interval)

    def _process_articles(self, articles: list):
        """Process a list of articles"""
        print(f"Found {len(articles)} new articles")
        articles_processed = 0

        for article in articles:
            article_url = article['url']
            print(f"Processing article: {article['title']}")
            print(f"URL: {article_url}")

            if self.article_processor.process_article(article_url):
                articles_processed += 1
                time.sleep(self.config.ARTICLE_PROCESSING_DELAY)

            print("-" * 80)

        print(f"Successfully processed {articles_processed} out of {len(articles)} articles")