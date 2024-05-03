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
# from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM
# from querent.config.core.gpt_llm_config import GPTConfig

# @pytest.mark.asyncio
# async def test_ingest_all_async():
#     # Set up the collectors
#     directories = [ "./tests/data/llm/predicate_checker"]
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
#     bert_llm_config = GPTConfig(
#     # ner_model_name="botryan96/GeoBERT",
#     enable_filtering=True,
#     openai_api_key="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",
#     filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#     ,fixed_entities = ["university", "greenwood", "liam zheng", "department", "Metroville", "Emily Stanton", "Coach", "health", "training", "atheletes" ]
#     ,sample_entities=["organization", "organization", "person",  "department", "city", "person", "person", "method", "method", "person"]
#     ,fixed_relationships=[
#     "Increase in research funding leads to environmental science focus",
#     "Dr. Emily Stanton's advocacy for cleaner energy",
#     "University's commitment to reduce carbon emissions",
#     "Dr. Stanton's research influences architectural plans",
#     "Collaborative project between sociology and environmental sciences",
#     "Student government launches mental health awareness workshops",
#     "Enhanced fitness programs improve sports teams' performance",
#     "Coach Torres influences student-athletes' holistic health",
#     "Partnership expands access to digital resources",
#     "Interdisciplinary approach enriches academic experience"
# ]
#             , sample_relationships=[
#     "Causal",
#     "Contributory",
#     "Causal",
#     "Influential",
#     "Collaborative",
#     "Initiative",
#     "Beneficial",
#     "Influential",
#     "Collaborative",
#     "Enriching"
# ],  
#             is_confined_search = True,
        
#     user_context="Your task is to analyze and interpret the context to construct semantic triples. The above context is from a  university document along with the identified entities using NER. Identify which entity is the subject entity and which is the object entity based on the context, and determine the meaningful relationship or predicate linking the subject entity to the object entity. Also identify the respective subject entity type , object entity and predicate type. Answer:"
#     )
#     llm_instance = GPTLLM(result_queue, bert_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             if event_state['event_type'] == EventType.Graph:
#                 triple = json.loads(event_state['payload'])
#                 print("triple: {}".format(triple))
#                 assert isinstance(triple['subject'], str) and triple['subject']
#             elif event_state['event_type'] == EventType.Vector:
#                 triple = json.loads(event_state['payload'])
#                 print("id: {}".format(triple['id']))
#                 print("namespace: {}".format(triple['namespace']))
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     llm_instance.subscribe(EventType.Vector, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
#     await asyncio.gather(ingest_task, querent_task)

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())
