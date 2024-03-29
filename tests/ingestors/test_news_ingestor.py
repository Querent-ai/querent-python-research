# import asyncio
# from pathlib import Path
# import pytest
# import os
# import uuid
# from dotenv import load_dotenv

# from querent.config.collector.collector_config import (
#     FSCollectorConfig,
#     DriveCollectorConfig,
#     NewsCollectorConfig,
#     SlackCollectorConfig,
# )
# from querent.common.uri import Uri
# from querent.ingestors.ingestor_manager import IngestorFactoryManager
# from querent.collectors.collector_resolver import CollectorResolver
# from querent.common.types.ingested_tokens import IngestedTokens


# load_dotenv()

# # Assuming you've set your News API key in an environment variable called NEWS_API_KEY
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# def news_collector_config():
#     # Example configuration for collecting news about "technology"
#     return NewsCollectorConfig(
#         config_source={
#         "id": str(uuid.uuid4()),
#         "name": "News API",
#         "api_key":NEWS_API_KEY,
#         "query":"Tesla",
#         "from_date":"2024-03-01",
#         "to_date":"2024-03-10",
#         "language":"en",
#         "sort_by":"publishedAt",
#         "page_size":5,
#         "page":1,
#         "config": {},
#         "uri": "news://"
#         }
#     )


# @pytest.mark.asyncio
# async def test_multiple_collectors_all_async():
#     # Set up the collectors
#     collectors = [
#         CollectorResolver().resolve(
#             Uri("news://"),
#             news_collector_config(),
#         )
#     ]

#     for collector in collectors:
#         await collector.connect()

#     # Set up the result queue
#     result_queue = asyncio.Queue()

#     # Create the IngestorFactoryManager
#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue
#     )

#     # Start the ingest_all_async in a separate task
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

#     # Wait for the task to complete
#     await asyncio.gather(ingest_task)

#     # Optionally, check the result_queue for ingested data
#     counter = 0
#     unique_files = set()
#     messages = 0
#     while not result_queue.empty():
#         ingested_data = await result_queue.get()
#         if ingested_data is not None:
#             if (
#                 isinstance(ingested_data, IngestedTokens)
#                 and ingested_data.is_token_stream
#             ):
#                 messages += 1
#             else:
#                 unique_files.add(ingested_data.file)
#             counter += 1
#     assert counter > 0



# if __name__ == "__main__":
#     asyncio.run(test_multiple_collectors_all_async())
