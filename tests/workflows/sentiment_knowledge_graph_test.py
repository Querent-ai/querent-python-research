# import asyncio
# import json
# from pathlib import Path
# import pytest
# import os
# import uuid
# from dotenv import load_dotenv

# from querent.callback.event_callback_interface import EventCallbackInterface
# from querent.common.types.querent_event import EventState, EventType
# from querent.config.collector.collector_config import (
#     FSCollectorConfig,
#     DriveCollectorConfig,
#     NewsCollectorConfig,
#     SlackCollectorConfig,
# )
# from querent.common.uri import Uri
# from querent.config.core.sentiment_config import Sentiment_Config
# from querent.core.transformers.sentiment_graph import Sentiment_Graph
# from querent.ingestors.ingestor_manager import IngestorFactoryManager
# from querent.collectors.collector_resolver import CollectorResolver
# from querent.common.types.ingested_tokens import IngestedTokens
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent


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
#         "query":"Tesla, Inc.",
#         "from_date":"2024-03-25",
#         "to_date":"2024-04-01",
#         "language":"en",
#         "sort_by":"publishedAt",
#         "page_size":5,
#         "page":1,
#         "config": {},
#         "uri": "news://"
#         }
#     )


# @pytest.mark.asyncio
# async def test_ingest_all_async():
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
#     # await asyncio.gather(ingest_task)
#     config = Sentiment_Config()
#     config.openai_api_key = "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"
#     config.huggingface_token="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"
#     # config.huggingface_api_url="https://api-inference.huggingface.co/models"
#     # config.sentiment_model_name="distilbert-base-uncased-finetuned-sst-2-english"
#     # Instantiate the DataPreprocessor class
#     llm_instance = Sentiment_Graph(result_queue, config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             # assert event_state.event_type == EventType.Graph
#             if event_state["event_type"] == EventType.Sentiment :
#                 triple = json.loads(event_state["payload"])
#                 print("file---------------------",event_state["file"], "----------------", type(event_state["file"]))
#                 print("triple: {}".format(triple))
#     llm_instance.subscribe(EventType.Sentiment, StateChangeCallback())
#     # llm_instance.subscribe(EventType.Vector, StateChangeCallback())
#     resource_manager = ResourceManager()
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
    
#     async def delayed_execution(result_queue):
#         await asyncio.sleep(5)  # Wait for 30 seconds
#         ingested_data = IngestedTokens(file="dummy_1_file.txt", data="Shares for Tesla are foing down because of widespread negativity")
#         await result_queue.put(ingested_data)
#     await asyncio.gather(ingest_task,querent_task, delayed_execution(result_queue))

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())