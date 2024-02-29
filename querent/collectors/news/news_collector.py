import asyncio
from newsapi import NewsApiClient
from typing import AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import CollectorConfig, CollectorBackend, NewsCollectorConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.uri import Uri
from querent.logging.logger import setup_logger

class NewsCollector(Collector):
    """Enhanced class for collecting news articles using NewsAPI with advanced search capabilities and pagination."""

    def __init__(self, config: NewsCollectorConfig):
        self.newsapi = NewsApiClient(api_key=config.api_key)
        self.config = config
        self.logger = setup_logger(__name__, "NewsCollector")

    async def connect(self):
        # Placeholder for future connection logic
        pass

    async def disconnect(self):
        # Placeholder for future disconnection cleanup logic
        pass

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        current_page = 1
        total_pages = float('inf')  # Assume an infinite number of pages initially

        while current_page <= total_pages:
            try:
                response = self.newsapi.get_everything(
                    q=self.config.query,
                    sources=self.config.sources,
                    domains=self.config.domains,
                    exclude_domains=self.config.exclude_domains,
                    from_param=self.config.from_date,
                    to=self.config.to_date,
                    language=self.config.language,
                    sort_by=self.config.sort_by,
                    page_size=self.config.page_size,
                    page=current_page
                )

                if response['status'] == 'ok':
                    articles = response.get('articles', [])
                    for article in articles:
                        article_data = {
                            "source": article.get('source', {}).get('name'),
                            "author": article.get('author'),
                            "title": article.get('title'),
                            "description": article.get('description'),
                            "url": article.get('url'),
                            "urlToImage": article.get('urlToImage'),
                            "publishedAt": article.get('publishedAt'),
                            "content": article.get('content')
                        }
                        yield CollectedBytes(file=article["title"], data=str(article_data).encode("utf-8"))
                        yield CollectedBytes(file=article["title"], data=None, error=None, eof=True)

                    total_results = response.get('totalResults', 0)
                    total_pages = (total_results + self.config.page_size - 1) // self.config.page_size  # Calculate total pages
                    current_page += 1
                else:
                    self.logger.error(f"News API request failed: {response.get('message')}")
                    break
            except Exception as e:
                self.logger.error(f"Error fetching news articles: {e}")
                yield CollectedBytes(file="Error", data=None, error=e)
                break

class NewsCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.News

    def resolve(self, uri: Uri, config: NewsCollectorConfig) -> Collector:
        return NewsCollector(config)
