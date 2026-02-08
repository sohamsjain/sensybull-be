"""
Entry point for RSS feed press release scraper
"""
from dotenv import load_dotenv
load_dotenv()

from .rss_scraper import RSSScraper
from .config import RSSConfig


def main():
    """Main entry point"""
    config = RSSConfig()
    scraper = RSSScraper(config)
    scraper.scrape_continuously()


if __name__ == "__main__":
    main()
