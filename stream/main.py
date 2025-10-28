"""
Entry point for Yahoo Finance scraper
"""
from .scraper import Scraper
from .config import Config


def main():
    """Main entry point"""
    # Initialize with default config
    config = Config()

    # Create and run scraper
    scraper = Scraper(config)
    scraper.scrape_continuously()


if __name__ == "__main__":
    main()