"""
Central orchestrator for all press release providers.

Manages concurrent polling of multiple providers via ThreadPoolExecutor.
Each provider runs in its own thread with its own polling interval.
Shared infrastructure (transformer, storage, HTTP client) handles
classification, persistence, and HTTP requests.
"""
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Set, Dict

from .http_client import HTTPClient
from .article_transformer import ArticleTransformer
from .storage_service import StorageService
from .feed_reader import FeedReader
from .providers.base import BaseProvider
from .config import PipelineConfig


class Orchestrator:
    """
    Multi-provider press release pipeline manager.

    Registers providers, spins up one thread per provider, and runs
    each provider's poll loop independently.  One provider failing
    never takes the others down.
    """

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()

        logging.basicConfig(
            level=self.config.LOG_LEVEL,
            format=self.config.LOG_FORMAT,
        )
        self.logger = logging.getLogger(__name__)

        # Shared infrastructure
        self.http_client = HTTPClient(self.config.HEADERS)
        self.transformer = ArticleTransformer()
        self.storage = StorageService(self.http_client, self.config.API_ENDPOINT)

        # Cross-provider dedup (thread-safe for set add/in via GIL)
        self.processed_urls: Set[str] = set()

        # Providers and their feed readers
        self.providers: List[BaseProvider] = []
        self.feed_readers: Dict[str, FeedReader] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register_provider(self, provider: BaseProvider):
        """Register a provider and optionally set up its RSS feed reader."""
        self.providers.append(provider)

        if provider.FEED_MODE == "rss" and provider.FEED_URL:
            self.feed_readers[provider.PROVIDER] = FeedReader(
                provider.FEED_URL,
                self.config.HEADERS,
            )

        self.logger.info(
            f"Registered provider: {provider.PROVIDER} "
            f"(mode={provider.FEED_MODE}, interval={provider.POLL_INTERVAL}s)"
        )

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """Start all provider polling loops concurrently (blocks forever)."""
        if not self.providers:
            self.logger.error("No providers registered — nothing to do.")
            return

        self.logger.info(
            f"Starting orchestrator with {len(self.providers)} providers: "
            f"{[p.PROVIDER for p in self.providers]}"
        )

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {
                executor.submit(self._provider_loop, provider): provider
                for provider in self.providers
            }
            # Each future is an infinite loop; as_completed only returns on crash
            for future in as_completed(futures):
                provider = futures[future]
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(
                        f"Provider {provider.PROVIDER} crashed unexpectedly: {e}",
                        exc_info=True,
                    )

    # ------------------------------------------------------------------
    # Per-provider loop
    # ------------------------------------------------------------------

    def _provider_loop(self, provider: BaseProvider):
        """Infinite polling loop for a single provider."""
        self.logger.info(f"[{provider.PROVIDER}] Polling loop started")

        while True:
            try:
                self._poll_provider(provider)
            except Exception as e:
                self.logger.error(
                    f"[{provider.PROVIDER}] Error during poll cycle: {e}",
                    exc_info=True,
                )

            self.logger.debug(
                f"[{provider.PROVIDER}] Sleeping {provider.POLL_INTERVAL}s..."
            )
            time.sleep(provider.POLL_INTERVAL)

    def _poll_provider(self, provider: BaseProvider):
        """Execute one poll cycle for a provider (RSS or scrape)."""
        if provider.FEED_MODE == "rss":
            self._poll_rss(provider)
        else:
            self._poll_scrape(provider)

    # ------------------------------------------------------------------
    # RSS-mode polling
    # ------------------------------------------------------------------

    def _poll_rss(self, provider: BaseProvider):
        reader = self.feed_readers.get(provider.PROVIDER)
        if not reader:
            self.logger.warning(f"[{provider.PROVIDER}] No feed reader configured")
            return

        items = reader.fetch_new_items()
        articles_processed = 0

        for item in items:
            url = item['link']
            if url in self.processed_urls:
                continue
            if self._process_article(provider, url, item):
                articles_processed += 1

        if articles_processed:
            self.logger.info(
                f"[{provider.PROVIDER}] Processed {articles_processed} new articles"
            )

    # ------------------------------------------------------------------
    # Scrape-mode polling
    # ------------------------------------------------------------------

    def _poll_scrape(self, provider: BaseProvider):
        html = self.http_client.get(provider.LISTING_URL)
        if not html:
            self.logger.warning(
                f"[{provider.PROVIDER}] Failed to fetch listing page: {provider.LISTING_URL}"
            )
            return

        items = provider.get_listing_urls(html)
        articles_processed = 0

        for item in items:
            url = item['link']
            if url in self.processed_urls:
                continue
            if self._process_article(provider, url, item):
                articles_processed += 1

        if articles_processed:
            self.logger.info(
                f"[{provider.PROVIDER}] Processed {articles_processed} new articles"
            )

    # ------------------------------------------------------------------
    # Single article processing
    # ------------------------------------------------------------------

    def _process_article(self, provider: BaseProvider, url: str, feed_item: dict) -> bool:
        """Fetch → parse → transform → store a single article. Returns True on success."""
        self.logger.info(f"[{provider.PROVIDER}] Processing: {feed_item.get('title', url)}")

        # 1. Fetch full article page
        html = self.http_client.get(url)
        if not html:
            self.logger.warning(f"[{provider.PROVIDER}] Failed to fetch: {url}")
            return False

        # 2. Provider-specific parsing
        article_data = provider.parse_article(url, html, feed_item)
        if not article_data:
            return False

        # 3. Skip articles with no recognized NYSE/NASDAQ tickers — they are noise
        if not article_data.get('tickers'):
            self.logger.info(
                f"[{provider.PROVIDER}] Skipping (no NYSE/NASDAQ tickers): {url}"
            )
            self.processed_urls.add(url)
            return False

        # 4. AI transformation (classification + summarization)
        try:
            title, bullets, summary, topic = self.transformer.transform(
                article_data['title'],
                article_data['article_text'],
            )
            article_data['title'] = title
            article_data['bullets'] = bullets
            article_data['summary'] = summary
            article_data['topics'] = [topic]
        except Exception as e:
            self.logger.error(f"[{provider.PROVIDER}] Transformer failed for {url}: {e}")
            text = article_data.get('article_text', '')
            article_data['bullets'] = []
            article_data['summary'] = (text[:500] + "...") if len(text) > 500 else text
            article_data['topics'] = ['General']

        article_data['extracted_at'] = datetime.now().isoformat()

        # 5. Persist
        saved = self.storage.save_article(article_data)
        if saved:
            self.processed_urls.add(url)

        time.sleep(self.config.ARTICLE_PROCESSING_DELAY)
        return saved
