"""
Web crawler for fetching documentation pages.

Downloads and saves HTML content from specified sources.
"""

import requests
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from src.config import Config


class WebCrawler:
    """Web crawler for downloading documentation pages."""

    def __init__(self, base_url: str = None, timeout: int = None, max_retries: int = None):
        """
        Initialize web crawler.

        Args:
            base_url: Base URL for crawling
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.base_url = base_url or Config.BASE_URL
        self.timeout = timeout or Config.CRAWLER_TIMEOUT
        self.max_retries = max_retries or Config.MAX_RETRIES
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": Config.USER_AGENT})
        self.output_dir = Path("./data/raw")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a single page with retry logic.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⚠️ Retry {attempt + 1}/{self.max_retries} for {url} (wait {wait_time}s)")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Failed to fetch {url}: {e}")
                    return None

    def save_page(self, url: str, content: str) -> Path:
        """
        Save page content to file.

        Args:
            url: Source URL
            content: HTML content

        Returns:
            Path to saved file
        """
        # Convert URL to filename
        parsed = urlparse(url)
        filename = parsed.path.strip("/").replace("/", "_") or "index"
        filename = f"{filename}.html"
        
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath

    def extract_links(self, html: str, base_url: str = None) -> List[str]:
        """
        Extract all links from HTML content.

        Args:
            html: HTML content
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []
        base = base_url or self.base_url

        for link in soup.find_all("a", href=True):
            url = urljoin(base, link["href"])
            # Filter to only same domain
            if urlparse(url).netloc == urlparse(self.base_url).netloc:
                links.append(url)

        return links

    def crawl_pages(self, urls: List[str], save_files: bool = True) -> List[tuple]:
        """
        Crawl multiple pages.

        Args:
            urls: List of URLs to crawl
            save_files: Whether to save HTML files

        Returns:
            List of tuples (url, content) for successfully fetched pages
        """
        results = []
        urls = list(set(urls))  # Remove duplicates

        for url in tqdm(urls, desc="Crawling"):
            content = self.fetch_page(url)
            if content:
                if save_files:
                    self.save_page(url, content)
                results.append((url, content))

        print(f"✅ Crawled {len(results)}/{len(urls)} pages successfully")
        return results

    def crawl_recursive(self, start_url: str, max_pages: int = 100, max_depth: int = 3):
        """
        Recursively crawl pages from a starting URL.

        Args:
            start_url: Starting URL
            max_pages: Maximum pages to crawl
            max_depth: Maximum recursion depth
        """
        visited = set()
        to_visit = [(start_url, 0)]
        results = []

        while to_visit and len(visited) < max_pages:
            url, depth = to_visit.pop(0)

            if url in visited or depth > max_depth:
                continue

            visited.add(url)
            print(f"Crawling ({len(visited)}/{max_pages}): {url}")

            content = self.fetch_page(url)
            if content:
                self.save_page(url, content)
                results.append((url, content))

                # Extract and queue new links
                if depth < max_depth:
                    links = self.extract_links(content, url)
                    for link in links:
                        if link not in visited:
                            to_visit.append((link, depth + 1))

        return results


def crawl_archlinux_docs(max_pages: int = 100) -> List[tuple]:
    """Helper function to crawl Arch Linux documentation."""
    crawler = WebCrawler()
    start_url = "https://wiki.archlinux.org/index.php"
    return crawler.crawl_recursive(start_url, max_pages=max_pages, max_depth=2)
