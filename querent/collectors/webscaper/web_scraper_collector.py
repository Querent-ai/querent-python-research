import asyncio
from aiohttp import ClientSession, TCPConnector
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import CollectorBackend, WebScraperConfig
from querent.common.uri import Uri
from querent.tools.web_page_extractor import WebpageExtractor
from urllib.parse import urlparse, urljoin


class WebScraperCollector(Collector):
    def __init__(self, config: WebScraperConfig):
        self.website_url = config.website_url
        self.semaphore = asyncio.Semaphore(
            5
        )  # Adjust the limit as needed (e.g., 5 requests at a time)
        self.poll_lock = asyncio.Lock()  # Lock for the poll method

    async def connect(self):
        pass  # Any setup logic before scraping

    async def disconnect(self):
        pass  # Any cleanup logic after scraping

    async def poll(self):
        async with self.poll_lock:
            urls_to_scrape = [self.website_url]
            while urls_to_scrape:
                url = urls_to_scrape.pop()
                content = await self.scrape_website(url)
                yield CollectedBytes(file=None, data=content.data, error=None)
                # Find and add links from this page to the list of URLs to scrape
                new_urls = self.extract_links(url)
                urls_to_scrape.extend(new_urls)

    async def scrape_website(self, website_url: str):
        async with self.semaphore:
            async with ClientSession(connector=TCPConnector(ssl=False)) as session:
                async with session.get(website_url) as response:
                    content = await response.text()
                    max_length = len(content)
                    return CollectedBytes(
                        data=content[:max_length], file=None, error=None
                    )

    def extract_links(self, base_url: str):
        # Use a proper HTML parser to extract links
        extractor = WebpageExtractor()
        links = extractor.extract_links(base_url)
        # Join relative links with the base URL
        return [urljoin(base_url, link) for link in links]


class WebScraperFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.WebScraper

    def resolve(self, uri: Uri, config: WebScraperConfig) -> Collector:
        return WebScraperCollector(config)
