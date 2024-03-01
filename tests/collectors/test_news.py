# import asyncio
# import pytest
# import os
# import uuid
# from querent.collectors.news.news_collector import NewsCollector
# from querent.common.uri import Uri
# from querent.config.collector.collector_config import NewsCollectorConfig
# from querent.collectors.collector_resolver import CollectorResolver

# # Assuming you've set your News API key in an environment variable called NEWS_API_KEY
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# @pytest.fixture
# def news_collector_config():
#     # Example configuration for collecting news about "technology"
#     return NewsCollectorConfig(
#         config_source={
#         "id": str(uuid.uuid4()),
#         "name": "News API",
#         "api_key":NEWS_API_KEY,
#         "query":"technology",
#         "from_date":"2024-02-01",
#         "to_date":"2024-02-28",
#         "language":"en",
#         "sort_by":"publishedAt",
#         "page_size":5,
#         "page":1,
#         "config": {},
#         "uri": "news://"
#         }
#     )

# @pytest.mark.asyncio
# async def test_news_collector_real_request(news_collector_config):
#     # Initialize the collector with the real API key and configuration
#     uri = Uri("news://")
#     resolver = CollectorResolver()
#     collector = resolver.resolve(uri, news_collector_config)
#     await collector.connect()

#     # Poll the collector and verify the response
#     async def poll_and_verify():
#         counter = 0
#         async for result in collector.poll():
#             assert result is not None
#             # Unwrap the CollectedBytes and verify its contents
#             data = result.unwrap() if result.data else None
#             if data:
#                 # Basic check to ensure we're getting article data back
#                 assert "title" in data.decode()
#                 counter += 1

#         # Ensure we received some articles
#         assert counter > 0

#     await poll_and_verify()

# if __name__ == "__main__":
#     asyncio.run(test_news_collector_real_request(news_collector_config()))
