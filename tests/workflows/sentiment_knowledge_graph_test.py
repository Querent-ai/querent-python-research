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
# # from querent.storage.neo4j_graphevent_storage import Neo4jConnection


# load_dotenv()

# # Assuming you've set your News API key in an environment variable called NEWS_API_KEY
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# def news_collector_config(query):
#     # Example configuration for collecting news about "technology"
#     return NewsCollectorConfig(
#         config_source={
#         "id": str(uuid.uuid4()),
#         "name": "News API",
#         "api_key":NEWS_API_KEY,
#         "query":query,
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
#     target_companies ={
#     # 'Nvidia Corporation': 'NVDA',
#     # 'Advanced Micro Devices': 'AMD',
#     # 'Meta Platforms, Inc.': 'META',
#     # 'Alphabet Inc.': 'GOOGL',
#     # 'Amazon.com, Inc.': 'AMZN',
#     # 'Intel Corporation': 'INTC',
#     # 'Microsoft Corporation': 'MSFT',
#     # 'Apple Inc.': 'AAPL',
#     # 'International Business Machines Corporation': 'IBM',
#     # 'Oracle Corporation': 'ORCL',
#     # 'Salesforce.com, inc.': 'CRM',
#     # 'Tesla, Inc.': 'TSLA',
#     # 'Uber Technologies, Inc.': 'UBER',
#     # 'Baidu, Inc.': 'BIDU',
#     # 'Qualcomm Incorporated': 'QCOM',
#     # 'Square, Inc.': 'SQ',
#     # 'Palantir Technologies Inc.': 'PLTR',
#     # 'Adobe Inc.': 'ADBE',
#     # 'Zoom Video Communications, Inc.': 'ZM',
#     # 'Splunk Inc.': 'SPLK',
#     # 'Shopify Inc.': 'SHOP',
#     # 'ServiceNow, Inc.': 'NOW',
#     # 'Snowflake Inc.': 'SNOW',
#     # 'Twilio Inc.': 'TWLO',
#     # 'DocuSign, Inc.': 'DOCU',
#     # 'CrowdStrike Holdings, Inc.': 'CRWD',
#     # 'Okta, Inc.': 'OKTA',
#     # 'Pinterest, Inc.': 'PINS',
#     # 'Broadcom Inc.': 'AVGO',
#     # 'Texas Instruments Incorporated': 'TXN'
# }

        
#     all_collectors = []
#         # Set up the collectors
#     for key, value in target_companies.items():
#         collector = CollectorResolver().resolve(
#                 Uri("news://"),
#                 news_collector_config(key),
#             )
#         all_collectors.append(collector)
#     for collector in all_collectors:
#         await collector.connect()

#     # Set up the result queue
#     result_queue = asyncio.Queue()

#     # Create the IngestorFactoryManager
#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=all_collectors, result_queue=result_queue
#     )

#     # Start the ingest_all_async in a separate task
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
#     # neo4j_uri = "neo4j+s://cab497eb.databases.neo4j.io"  # Change this to your Neo4j instance
#     # neo4j_user = "neo4j"  # Change to your Neo4j username
#     # neo4j_password = "1Tu6xeT3Wyp2Eu9spLhuC5G7X9ypw6LNjhMPZt7a9Xw"  # Change to your Neo4j password
#     # neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    
#     # Wait for the task to complete
#     # await asyncio.gather(ingest_task)
#     config = Sentiment_Config()
#     config.openai_api_key = "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"
#     config.huggingface_token="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"
#     # config.huggingface_api_url="https://api-inference.huggingface.co/models"
#     config.sentiment_model_name="distilbert-base-uncased-finetuned-sst-2-english"
#     # Instantiate the DataPreprocessor class
#     llm_instance = Sentiment_Graph(result_queue, config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             # assert event_state.event_type == EventType.Graph
#             if event_state["event_type"] == EventType.Sentiment :
#                 triple = json.loads(event_state["payload"])
#                 print("file---------------------",event_state["file"], "----------------", type(event_state["file"]))
#                 print("triple: {}".format(triple))
#                 # neo4j_conn.insert_sentiment_graph_event(triple)
                
#     llm_instance.subscribe(EventType.Sentiment, StateChangeCallback())
#     # llm_instance.subscribe(EventType.Vector, StateChangeCallback())
#     resource_manager = ResourceManager()
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
    
#     async def delayed_execution(result_queue):
#         await asyncio.sleep(1)  # Wait for 30 seconds
#         ingested_data = IngestedTokens(file="dummy_1_file.txt", data="Shares for Tesla are foing down because of widespread negativity")
#         await result_queue.put(ingested_data)
#         ingested_data = IngestedTokens(file="dummy_2_file.txt", data="Shares for Tesla are foing down because of widespread negativity")
#         await result_queue.put(ingested_data)
#         ingested_data = IngestedTokens(file="dummy_3_file.txt", data="Shares for Tesla are foing down because of widespread negativity")
#         await result_queue.put(ingested_data)
#         ingested_data = IngestedTokens(file="dummy_4_file.txt", data="Shares for Tesla are going up")
#         await result_queue.put(ingested_data)
#     await asyncio.gather(delayed_execution(result_queue),querent_task, ingest_task)
#     # await asyncio.gather(ingest_task,querent_task)
#     # neo4j_conn.close()

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())