import requests
from bs4 import BeautifulSoup
import logging
import time
import json
import os
from datetime import datetime, UTC
import re
from html import unescape


class YahooFinancePaginatedScraper:
    def __init__(self, output_file="yahoo_finance_articles.json"):
        self.base_url = "https://finance.yahoo.com/sitemap"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.output_file = output_file

        # Create output file if it doesn't exist
        if not os.path.exists(output_file):
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Store seen articles to avoid duplicates
        self.seen_articles = set()
        self.processed_articles = set()

    def get_today_date_string(self):
        """Get today's date in the format used by Yahoo Finance sitemap"""
        return datetime.now(UTC).strftime("%Y_%m_%d")

    def get_initial_url(self):
        """Generate the initial URL for today's sitemap"""
        date_str = self.get_today_date_string()
        return f"{self.base_url}/{date_str}_start"

    def extract_next_page_token(self, current_url):
        """Extract the next page token from pagination link"""
        try:
            soup = BeautifulSoup(self.fetch_page(current_url), 'html.parser')
            next_link = soup.find('a', string='Next')

            if next_link and 'href' in next_link.attrs:
                next_url = next_link['href']
                # Extract the token number from the URL
                match = re.search(r'start(\d+)$', next_url)
                if match:
                    return match.group(1)
        except Exception as e:
            self.logger.error(f"Error extracting next page token: {e}")
        return None

    def fetch_page(self, url):
        """Fetch and return the content of a page"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            self.logger.error(f"Error fetching page {url}: {e}")
            return None

    def extract_article_links(self, html_content):
        """Extract article links from the sitemap page"""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        articles = []

        # Find all article links in the sitemap
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Only include news article links and exclude navigation links
            if '/news/' in href and href not in self.seen_articles:
                # Make sure URL is absolute
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

    def extract_article_data(self, article_url):
        """Extract article data from a Yahoo Finance article URL"""
        try:
            # Fetch the article page
            html_content = self.fetch_page(article_url)
            if not html_content:
                self.logger.error(f"Failed to fetch article content from {article_url}")
                return None

            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Get article URL path for pattern matching
            url_path = article_url.split("/news/")[1] if "/news/" in article_url else ""
            pattern = re.compile(url_path)

            # Find the script tag containing article data
            def has_data_url(tag):
                if 'data-url' in tag.attrs and isinstance(tag['data-url'], str):
                    return pattern.search(tag['data-url'])
                return False

            # Find matching script elements
            matching_elements = soup.find_all(has_data_url)
            if not matching_elements:
                self.logger.error(f"Could not find article data script for {article_url}")
                return None

            # Extract JSON data from script
            script = matching_elements[0]
            try:
                # Parse nested JSON structure
                data = json.loads(script.contents[0])
                data = json.loads(data.get('body', '{}'))

                # Extract article data
                items = data.get('items', [])
                if not items:
                    self.logger.error(f"No items found in article data for {article_url}")
                    return None

                article_data = items[0].get('data', {})
                content_meta = article_data.get('contentMeta', {})

                # Extract required fields
                # 1. Timestamp
                dates = content_meta.get('dates', {})
                display_date = dates.get('displayDate', {})
                timestamp = display_date.get('timestamp')
                if not timestamp:
                    self.logger.error(f"No timestamp found for {article_url}")
                    return None

                # 2. Title
                seo_meta = content_meta.get('seoMeta', {})
                title = seo_meta.get('title')
                if not title:
                    self.logger.error(f"No title found for {article_url}")
                    return None

                # 3. Provider information
                provider_url = seo_meta.get('providerContentUrl')
                if provider_url:
                    provider = content_meta.get('attribution', {}).get('provider', {}).get('name')
                else:
                    provider_url = seo_meta.get('canonicalUrl')
                    provider = "Yahoo Finance"

                if not provider or not provider_url:
                    self.logger.error(f"No provider information found for {article_url}")
                    return None

                # 4. Summary
                content_summaries = content_meta.get('contentSummaries', {})
                summary = content_summaries.get('summary')
                if not summary:
                    self.logger.error(f"No summary found for {article_url}")
                    return None

                # 5. Image
                content_images = content_meta.get('contentImages', {})
                primary_image = content_images.get('primaryImage', {})
                if not primary_image:
                    self.logger.error(f"No primary image found for {article_url}")
                    return None

                original_image = primary_image.get('original', {})
                image_url = original_image.get('url')
                if not image_url:
                    self.logger.error(f"No image URL found for {article_url}")
                    return None

                # 6. Tickers (optional)
                tickers = []
                content_tags = content_meta.get('contentTags', {})
                xray_meta = content_tags.get('xrayMeta', [])
                for item in xray_meta:
                    if item.get('type') == 'ticker':
                        tickers.append(item.get('id'))

                # 7. Article text
                story_atoms = content_meta.get('storyAtoms', [])
                article_text = ''
                for atom in story_atoms:
                    if atom.get('type') == 'text':
                        content = atom.get('content', '')
                        # Remove HTML tags and decode entities
                        clean_content = re.sub(r'<[^>]+>', '', unescape(content))
                        if clean_content:
                            article_text += clean_content + "\n\n"

                # Create article object
                article = {
                    'url': article_url,
                    'title': title,
                    'timestamp': timestamp,
                    'provider': provider,
                    'provider_url': provider_url,
                    'summary': summary,
                    'image_url': image_url,
                    'tickers': tickers,
                    'article_text': article_text.strip(),
                    'extracted_at': datetime.now().isoformat()
                }

                return article

            except (json.JSONDecodeError, IndexError, KeyError, AttributeError) as e:
                self.logger.error(f"Error parsing article data for {article_url}: {e}")
                return None

        except Exception as e:
            self.logger.error(f"Unexpected error extracting article data from {article_url}: {e}")
            return None

    def save_article(self, article):
        """Save an article to the output JSON file"""
        try:

            response = requests.post(
                "http://localhost:5000/articles",
                headers={"Content-Type": "application/json"},
                data=json.dumps(article)
            )

            # Check if the request was successful
            if response.status_code == 201:
                self.logger.info(f"Article stored successfully!: {article['url']}")
                return True
            else:
                self.logger.info(f"Error: {response.status_code}")
                self.logger.info(f"Article storing failed!: {article['url']}")
                return False

        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False

    def process_article(self, article_url):
        """Process a single article URL - extract data and save it"""
        if article_url in self.processed_articles:
            self.logger.info(f"Skipping already processed article: {article_url}")
            return False

        self.logger.info(f"Processing article: {article_url}")
        article_data = self.extract_article_data(article_url)

        if article_data:
            self.save_article(article_data)
            self.processed_articles.add(article_url)
            return True
        else:
            self.logger.warning(f"Failed to extract valid data for article: {article_url}")
            return False

    def scrape_continuously(self, interval=10, page_retry_interval=60):
        """Continuously scrape the sitemap pages"""
        current_date = self.get_today_date_string()

        while True:
            try:
                # Get initial URL for the current date
                current_url = f"{self.base_url}/{current_date}_start"
                print(f"Starting scrape cycle with URL: {current_url}")

                page_without_next = None  # Track the last page with no "Next" link

                while current_url:
                    # Fetch and process current page
                    html_content = self.fetch_page(current_url)
                    if not html_content:
                        print("Failed to fetch page content.")
                        time.sleep(interval)
                        break

                    articles = self.extract_article_links(html_content)

                    # Log and process found articles
                    if articles:
                        print(f"Found {len(articles)} new articles")
                        articles_processed = 0

                        for article in articles:
                            article_url = article['url']
                            print(f"Processing article: {article['title']}")
                            print(f"URL: {article_url}")

                            # Extract and save article data
                            if self.process_article(article_url):
                                articles_processed += 1
                                # Add a small delay between article processing
                                time.sleep(1)

                            print("-" * 80)

                        print(f"Successfully processed {articles_processed} out of {len(articles)} articles")

                    # Get next page token
                    next_token = self.extract_next_page_token(current_url)

                    if next_token:
                        # Move to next page with pagination token
                        current_url = f"{self.base_url}/{current_date}_start{next_token}"
                        print(f"Moving to next page: {current_url}")
                        page_without_next = None  # Reset this since we found a next page
                        # Small delay between pages
                        time.sleep(2)
                    else:
                        # No next page found
                        # Check if the date has changed
                        new_date = self.get_today_date_string()
                        if new_date != current_date:
                            print(f"Date changed from {current_date} to {new_date}. Starting fresh cycle.")
                            current_date = new_date
                            break  # Exit inner loop to start with the new date

                        # Date hasn't changed - we've reached the last page for now
                        if page_without_next != current_url:
                            # First time seeing this page without a next link
                            page_without_next = current_url
                            print(
                                f"Reached last available page. Will retry this page in {page_retry_interval} seconds.")

                        # Wait longer before retrying the same page
                        time.sleep(page_retry_interval)

                        # We don't change current_url, so the loop will retry the same page
                        print(f"Retrying last page to check for new content: {current_url}")

                # Only reach here if we broke out of the inner loop
                # Either to start a new date, or there was an error
                print(f"Completed cycle. Waiting {interval} seconds before checking again...")
                time.sleep(interval)

            except Exception as e:
                print(f"Error in scrape cycle: {e}")
                time.sleep(interval)


# Example usage
if __name__ == "__main__":
    scraper = YahooFinancePaginatedScraper(output_file="yahoo_finance_articles.json")
    scraper.scrape_continuously()