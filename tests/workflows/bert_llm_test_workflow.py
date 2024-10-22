# import asyncio
# from asyncio import Queue
# import json
# from pathlib import Path
# from querent.callback.event_callback_interface import EventCallbackInterface
# from querent.collectors.fs.fs_collector import FSCollectorFactory
# from querent.common.types.ingested_tokens import IngestedTokens
# from querent.common.types.querent_event import EventState, EventType
# from querent.config.collector.collector_config import FSCollectorConfig
# from querent.common.uri import Uri
# from querent.config.core.llm_config import LLM_Config
# from querent.ingestors.ingestor_manager import IngestorFactoryManager
# import pytest
# import uuid
# from querent.common.types.file_buffer import FileBuffer
# from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent
# import time

# @pytest.mark.asyncio
# async def test_ingest_all_async():
#     # Set up the collectors
#     directories = [ "./tests/data/llm/one_file/"]
#     collectors = [
#         FSCollectorFactory().resolve(
#             Uri("file://" + str(Path(directory).resolve())),
#             FSCollectorConfig(config_source={
#                     "id": str(uuid.uuid4()),
#                     "root_path": directory,
#                     "name": "Local-config",
#                     "config": {},
#                     "backend": "localfile",
#                     "uri": "file://",
#                 }),
#         )
#         for directory in directories
#     ]

#     # Set up the result queue
#     result_queue = asyncio.Queue()

#     # Create the IngestorFactoryManager
#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue
#     )
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
#     resource_manager = ResourceManager()
#     bert_llm_config = LLM_Config(
#     ner_model_name="botryan96/GeoBERT",
#     enable_filtering=True,
#     filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         },
#     user_context="Query: Your task is to analyze and interpret the context to construct semantic triples. The above context is from a geological research study on reservoirs and the above entities and their respective types have already been identified. Please Identify the entity which is the subject and the entity which is object based on the context, and determine the meaningful relationship or predicate linking the subject entity to the object entity. Determine whether the entity labels provided match the subject type and object type and correct if needed. Also provide the predicate type. Answer:"
#     )
#     llm_instance = BERTLLM(result_queue, bert_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             assert event_state['event_type'] == EventType.Graph
#             triple = json.loads(event_state['payload'])
#             print("triple: {}".format(triple))
#             assert isinstance(triple['subject'], str) and triple['subject']
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
#     await asyncio.gather(ingest_task, querent_task)

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())
