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
# from querent.core.transformers.fixed_entities_set_opensourcellm import Fixed_Entities_LLM
# from querent.ingestors.ingestor_manager import IngestorFactoryManager
# import pytest
# import uuid
# from querent.common.types.file_buffer import FileBuffer
# from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
# from querent.processors.text_cleanup_processor import TextCleanupProcessor
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent
# import time
# # from querent.storage.milvus_vectorevent_storage import MilvusDBConnection
# from querent.config.core.gpt_llm_config import GPTConfig
# from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM

# @pytest.mark.asyncio
# async def test_ingest_all_async():
#     # Set up the collectors
#     # db_conn = DatabaseConnection(dbname="postgres", 
#     #         user="postgres", 
#     #         password="querent", 
#     #         host="localhost", 
#     #         port="5432")
#     # # ml_conn = MilvusDBConnection()
#     directories = [ "/home/nishantg/querent-main/querent/tests/data/image"]
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
#     text_cleanup_processor = TextCleanupProcessor()
#     # Create the IngestorFactoryManager
#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue, processors=[text_cleanup_processor]
#     )
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
#     resource_manager = ResourceManager()
#     gpt_llm_config = LLM_Config(
#     ner_model_name="botryan96/GeoBERT",
#     # rel_model_path="/home/nishantg/Downloads/openhermes-2.5-mistral-7b.Q5_K_M.gguf",
#     enable_filtering=True
#     # openai_api_key="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"
#     ,filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#     #   ,fixed_entities =["geologists", "Earth","asphaltene", "Eagle ford", "Nitrogen", "industry"],
#     #  sample_entities = ["method", "method", "method", "method", "method"]
            
#     ,user_context="Query: Your task is to analyze and interpret the context to construct semantic triples. Please Identify the entity which is the subject and the entity which is object based on the context, and determine the meaningful relationship or predicate linking the subject entity to the object entity. Determine whether the entity labels provided match the subject type and object type and correct if needed. Also provide the predicate type. Answer:"
#     # ,fixed_entities =["modeling", "sonic", "symmetry","isotropy", "Carbonate", "Clastic", "Porosity", "Permeability", "Oil saturation", "Water saturation", "Gas saturation", "Depth", "Size", "Temperature", "Pressure", "Oil viscosity", "Gas-oil ratio", "Water cut", "Recovery factor", "Enhanced recovery technique", "Horizontal drilling", "Hydraulic fracturing", "Water injection", "Gas injection", "Steam injection", "Seismic activity", "Structural deformation", "Faulting", "Cap rock integrity", "Compartmentalization", "Connectivity", "Production rate", "Depletion rate", "Exploration technique", "Drilling technique", "Completion technique", "Environmental impact", "Regulatory compliance", "Economic analysis", "Market analysis", "oil well", "gas well", "oil field", "Gas field", "eagle ford shale", "ghawar", "johan sverdrup", "karachaganak", "maracaibo"],
#     # sample_entities = ["method","method","method","method", "rock_type", "rock_type", "reservoir_property", "reservoir_property", "reservoir_property", "reservoir_property", "reservoir_property", "reservoir_characteristic", "reservoir_characteristic", "reservoir_characteristic", "reservoir_characteristic", "reservoir_property", "reservoir_property", "production_metric", "production_metric", "recovery_technique", "drilling_technique", "recovery_technique", "recovery_technique", "recovery_technique", "recovery_technique", "geological_feature", "geological_feature", "geological_feature", "reservoir_feature", "reservoir_feature", "reservoir_feature", "production_metric", "production_metric", "exploration_method", "drilling_method", "completion_method", "environmental_aspect", "regulatory_aspect", "economic_aspect", "economic_aspect", "hydrocarbon_source", "hydrocarbon_source", "hydrocarbon_source", "hydrocarbon_source", "reservoir", "reservoir", "reservoir", "reservoir", "reservoir"]
#             # , is_confined_search = True
#     )
#     llm_instance = BERTLLM(result_queue, gpt_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             # assert event_state.event_type == EventType.Graph
#             if event_state['event_type'] == EventType.Graph :
#                 triple = json.loads(event_state['payload'])
#                 print("file---------------------",event_state['file'], "----------------", type(event_state['file']))
#                 print("triple: {}".format(triple))
#                 graph_event_data = {
#             'subject': triple['subject'],
#             'subject_type': triple['subject_type'],
#             'object': triple['object'],
#             'object_type': triple['object_type'],
#             'predicate': triple['predicate'],
#             'predicate_type': triple['predicate_type'],
#             'sentence': triple['sentence'],
#             'document_id': event_state['file']
#         }
#                 # db_conn.insert_graph_event(graph_event_data)
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
#     await asyncio.gather(ingest_task, querent_task)
#     # db_conn.close()

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())
