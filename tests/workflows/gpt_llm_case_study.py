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
# from querent.config.core.gpt_llm_config import GPTConfig
# from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM
# from querent.ingestors.ingestor_manager import IngestorFactoryManager
# import pytest
# import uuid
# from querent.common.types.file_buffer import FileBuffer
# from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent
# import time
# from querent.storage.postgres_graphevent_storage import DatabaseConnection
# from querent.storage.milvus_vectorevent_storage import MilvusDBConnection

# @pytest.mark.asyncio
# async def test_ingest_all_async():
#     # Set up the collectors
#     db_conn = DatabaseConnection(dbname="postgres", 
#             user="querent", 
#             password="querent", 
#             host="localhost", 
#             port="5432")
#     # ml_conn = MilvusDBConnection()
#     directories = [ "/path/to/directory"]
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
#     print("Going to start ingesting now.......")
#     resource_manager = ResourceManager()
#     bert_llm_config = GPTConfig(
#     ner_model_name="botryan96/GeoBERT",
#     rel_model_path="/path/to/model.gguf",
#     enable_filtering=True,
#     filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#             ,fixed_entities = [
#                     "Reservoir", "Pore pressure", "Ground water",
#                     "Carbonate rock", "Clastic rock", "Porosity", "Permeability",
#                     "Oil saturation", "Water saturation", "Gas saturation",
#                     "Depth", "Size", "Temperature",
#                     "Pressure", "Oil viscosity", "Gas-oil ratio",
#                     "Water cut", "Recovery factor", "Enhanced recovery technique",
#                     "Horizontal drilling", "Hydraulic fracturing", "Water injection", "Gas injection", "Steam injection",
#                     "Seismic activity", "Structural deformation", "Faulting",
#                     "Cap rock integrity", "Compartmentalization",
#                     "Connectivity", "Production rate", "Depletion rate",
#                     "Exploration technique", "Drilling technique", "Completion technique",
#                     "Environmental impact", "Regulatory compliance",
#                     "Economic analysis", "Market analysis"
#                 ]

#             , sample_entities = [
#                     "reservoir", "reservoir_property", "ground_water",
#                     "rock_type", "rock_type", "reservoir_property", "reservoir_property",
#                     "reservoir_property", "reservoir_property", "reservoir_property",
#                     "reservoir_characteristic", "reservoir_characteristic", "reservoir_characteristic",
#                     "reservoir_characteristic", "reservoir_property", "reservoir_property",
#                     "production_metric", "production_metric", "recovery_technique",
#                     "drilling_technique", "recovery_technique", "recovery_technique", "recovery_technique", "recovery_technique",
#                     "geological_feature", "geological_feature", "geological_feature",
#                     "reservoir_feature", "reservoir_feature",
#                     "reservoir_feature", "production_metric", "production_metric",
#                     "exploration_method", "drilling_method", "completion_method",
#                     "environmental_aspect", "regulatory_aspect",
#                     "economic_aspect", "economic_aspect"
#                 ]
#             , is_confined_search = True,
#             openai_api_key = "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",
#             # , huggingface_token = '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'
#             user_context = """Query: The above context is from a geological research paper on reservoirs and the above entities and their respective types have already been identified.
#             Please Identify the entity which is the subject and which is object from the above entities based on the context, and determine the predicate linking them, utilizing a semantic triple framework (Subject, Predicate, Object). Also, classify the predicate according to geology-specific types.
# Answer:"""
#     )
#     llm_instance = GPTLLM(result_queue, bert_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             # assert event_state.event_type == EventType.Graph
#             if event_state["event_type"] == EventType.Graph :
#                 triple = json.loads(event_state["payload"])
#                 print("file---------------------",event_state["file"], "----------------", type(event_state["file"]))
#                 print("triple: {}".format(triple))
#                 graph_event_data = {
#             'subject': triple['subject'],
#             'subject_type': triple['subject_type'],
#             'object': triple['object'],
#             'object_type': triple['object_type'],
#             'predicate': triple['predicate'],
#             'predicate_type': triple['predicate_type'],
#             'sentence': triple['sentence'],
#             'document_id': event_state["file"]
#         }
#                 db_conn.insert_graph_event(graph_event_data)
#                 assert isinstance(triple['subject'], str) and triple['subject']
#             # else :
#             #     vector_triple = json.loads(event_state.payload)
#             #     print("Inside Vector event ---------------------------------", vector_triple)
#             #     milvus_coll = ml_conn.create_collection(collection_name=vector_triple['namespace'],dim = 384)
#             #     ml_conn.insert_vector_event(id = vector_triple['id'], embedding= vector_triple['embeddings'], namespace= vector_triple['namespace'], document=event_state.file, collection= milvus_coll )
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     # llm_instance.subscribe(EventType.Vector, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
#     await asyncio.gather(querent_task, ingest_task)
#     db_conn.close()

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())