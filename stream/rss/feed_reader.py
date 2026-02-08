"""
Generic RSS feed reader using feedparser
"""
import feedparser
import logging
import time
import calendar
from typing import List, Dict, Optional


class FeedReader:
    """Fetches and parses RSS feeds, tracking seen items to yield only new ones"""

    def __init__(self, feed_url: str, headers: dict = None):
        self.feed_url = feed_url
        self.headers = headers or {}
        self.seen_guids: set = set()
        self.logger = logging.getLogger(__name__)

    def fetch_new_items(self) -> List[Dict]:
        """
        Fetch the RSS feed and return only items not seen before.

        Returns:
            List of dicts with keys: title, link, description, published (unix ts), guid
        """
        feed = feedparser.parse(self.feed_url, request_headers=self.headers)

        if feed.bozo:
            self.logger.warning(f"Feed parsing issue: {feed.bozo_exception}")

        if not feed.entries:
            self.logger.info(f"No entries found in feed: {self.feed_url}")
            return []

        new_items = []
        for entry in feed.entries:
            guid = entry.get('id') or entry.get('link', '')

            if guid in self.seen_guids:
                continue

            self.seen_guids.add(guid)
            new_items.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'description': entry.get('description', ''),
                'published': self._parse_timestamp(entry),
                'guid': guid,
            })

        self.logger.info(f"Fetched {len(feed.entries)} items, {len(new_items)} new from {self.feed_url}")
        return new_items

    def _parse_timestamp(self, entry) -> int:
        """Convert feed entry date to unix timestamp in milliseconds (to match Yahoo pipeline)"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return int(calendar.timegm(entry.published_parsed)) * 1000
        return int(time.time()) * 1000
