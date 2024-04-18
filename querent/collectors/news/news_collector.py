import asyncio
import datetime
import uuid
from newsapi import NewsApiClient
from typing import AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import (
    CollectorBackend,
    NewsCollectorConfig,
)
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
        total_pages = float("inf")  # Assume an infinite number of pages initially

        # Adjust to_date for special cases to the current date
        should_keep_going = False
        if self.config.to_date in ["now", "latest", "", "present"]:
            should_keep_going = True

        if should_keep_going:
            while should_keep_going:
                if should_keep_going:
                    self.config.to_date = datetime.datetime.now().strftime("%Y-%m-%d")
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
                            page=current_page,
                        )
                        if response["status"] == "ok":
                            articles = response.get("articles", [])
                            if not articles:
                                # If no articles found, consider sleeping for a shorter duration
                                await asyncio.sleep(3600)  # Example: 1 hour
                                continue

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
                                publish_date = article.get('publishedAt').split('T')[0]

                                title = article['title']
                                yield CollectedBytes(file=f"{self.config.query}_{publish_date}.news", data=str(article_data).encode("utf-8"), doc_source=f"news://{self.config.query}")
                                yield CollectedBytes(file=f"{self.config.query}_{publish_date}.news", data=None, error=None, eof=True, doc_source=f"news://{self.config.query}")

                            total_results = response.get("totalResults", 0)
                            total_pages = (
                                total_results + self.config.page_size - 1
                            ) // self.config.page_size
                            current_page += 1
                        else:
                            self.logger.error(
                                f"News API request failed: {response.get('message')}"
                            )
                            break
                    except Exception as e:
                        self.logger.error(f"Error fetching news articles: {e}")
                        yield CollectedBytes(file="Error", data=None, error=e, doc_source=f"news://{self.config.query}")
                        break

                # After exhausting the current batch, reset for next polling cycle
                current_page = 1
                total_pages = float("inf")
                if not should_keep_going:
                    break
                # Adjust the to_date for the next cycle
                self.config.from_date = self.config.to_date
                await asyncio.sleep(86400)
        else:
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
                    page=current_page,
                )
                if response["status"] == "ok":
                    articles = response.get("articles", [])
                    if not articles:
                        return

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

                        publish_date = article.get('publishedAt').split('T')[0]
                        title = article['title']
                        yield CollectedBytes(file=f"{self.config.query}_{publish_date}.news", data=str(article_data).encode("utf-8"), doc_source=f"news://{self.config.query}")
                    yield CollectedBytes(file=f"{self.config.query}_{publish_date}.news", data=None, error=None, eof=True, doc_source=f"news://{self.config.query}")
            except Exception as e:
                self.logger.error(f"Error fetching news articles: {e}")




class NewsCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.News

    def resolve(self, uri: Uri, config: NewsCollectorConfig) -> Collector:
        return NewsCollector(config)
