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
# from querent.storage.postgres_graphevent_storage import DatabaseConnection
# from querent.storage.milvus_vectorevent_storage import MilvusDBConnection
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
#     text_cleanup_processor = TextCleanupProcessor()
#     # Create the IngestorFactoryManager
#     ingestor_factory_manager = IngestorFactoryManager(
#         collectors=collectors, result_queue=result_queue, processors=[text_cleanup_processor]
#     )
#     ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())
#     resource_manager = ResourceManager()
#     gpt_llm_config = GPTConfig(
#     ner_model_name="botryan96/GeoBERT",
#     rel_model_path="/home/nishantg/Downloads/openhermes-2.5-mistral-7b.Q5_K_M.gguf",
#     enable_filtering=True,
#     filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#     ,fixed_entities = [
#                     "Hadean", "Archean", "Proterozoic", "Phanerozoic",
#                     "Paleozoic", "Mesozoic", "Cenozoic",
#                     "Cambrian", "Ordovician", "Silurian", "Devonian", "Carboniferous", "Permian",
#                     "Triassic", "Jurassic", "Cretaceous",
#                     "Paleogene", "Neogene", "Quaternary",
#                     "Paleocene", "Eocene", "Oligocene",
#                     "Miocene", "Pliocene",
#                     "Pleistocene", "Holocene",
#                     "Anticline", "Syncline", "Fault", "Salt dome", "Horst", "Graben",
#                     "Reef", "Shoal", "Deltaic deposits", "Turbidite", "Channel sandstone",
#                     "Sandstone", "Limestone", "Dolomite", "Shale",
#                     "Source rock", "Cap rock", "Shale gas",
#                     "Crude oil", "Natural gas", "Shale oil", "Coalbed methane", "Tar sands", "Gas hydrates",
#                     "Structural trap", "Stratigraphic trap", "Combination trap", "Salt trap", "Unconformity trap",
#                     "Hydrocarbon migration", "Hydrocarbon accumulation",
#                     "Placer deposits", "Vein deposit", "Porphyry deposit", "Kimberlite pipe", "Laterite deposit",
#                     "Volcanic rock", "Basalt", "Geothermal gradient", "Sedimentology",
#                     "Paleontology", "Biostratigraphy", "Sequence stratigraphy", "Geophysical survey",
#                     "Magnetic anomaly", "Gravitational anomaly", "Petrology", "Geochemistry", "Hydrogeology"
#                 ]

#     , sample_entities=[
#                     "geological_eon", "geological_eon", "geological_eon", "geological_eon",
#                     "geological_era", "geological_era", "geological_era",
#                     "geological_period", "geological_period", "geological_period", "geological_period", "geological_period", "geological_period",
#                     "geological_period", "geological_period", "geological_period",
#                     "geological_period", "geological_period", "geological_period",
#                     "geological_epoch", "geological_epoch", "geological_epoch",
#                     "geological_epoch", "geological_epoch",
#                     "geological_epoch", "geological_epoch", "structural_feature", "structural_feature", "structural_feature", "structural_feature", "structural_feature", "structural_feature",
#                     "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature",
#                     "rock_type", "rock_type", "rock_type", "rock_type",
#                     "rock_type", "rock_type", "hydrocarbon_source",
#                     "hydrocarbon", "hydrocarbon", "hydrocarbon", "hydrocarbon", "hydrocarbon", "hydrocarbon",
#                     "trap_type", "trap_type", "trap_type", "trap_type", "trap_type",
#                     "geological_process", "geological_process",
#                     "mineral_deposit", "mineral_deposit", "mineral_deposit", "mineral_deposit", "mineral_deposit",
#                     "rock_type", "rock_type", "geological_process", "geological_discipline",
#                     "geological_discipline", "geological_method", "geological_method", "geological_method",
#                     "geophysical_feature", "geophysical_feature", "geological_discipline", "geological_discipline", "geological_discipline"
#                 ]
#             , is_confined_search = True
#             # , huggingface_token = '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'
#     )
#     llm_instance = GPTLLM(result_queue, gpt_llm_config)
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
