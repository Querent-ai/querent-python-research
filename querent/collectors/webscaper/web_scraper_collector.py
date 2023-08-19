from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.config.collector_config import CollectorBackend, WebScraperConfig
from querent.tools.web_page_extractor import WebpageExtractor
from querent.common.uri import Uri

class WebScraperCollector(Collector):
    def __init__(self, config: WebScraperConfig):
        self.website_url = config.website_url

    async def connect(self):
        pass  # Any setup logic before scraping

    async def disconnect(self):
        pass  # Any cleanup logic after scraping

    async def poll(self):
        content = await self.scrape_website(self.website_url)
        yield CollectorResult(content)

    async def scrape_website(self, website_url: str):
        content = WebpageExtractor().extract_with_bs4(website_url)
        max_length = len(' '.join(content.split(" ")[:600]))
        return content[:max_length]

class WebScraperFactory(CollectorFactory):
    def __init__(self):
        pass
    
    def backend(self) -> CollectorBackend:
        return CollectorBackend.WebScraper

    def resolve(self,uri: Uri, config: WebScraperConfig) -> Collector:
        return WebScraperCollector(config)
