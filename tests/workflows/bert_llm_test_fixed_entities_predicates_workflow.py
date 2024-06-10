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
# from .Postgres_new_algo import DatabaseManager
# from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
# import numpy as np

# @pytest.mark.asyncio
# async def test_ingest_all_async():
#     db_manager = DatabaseManager(
#         dbname="querent_test",
#         user="querent",
#         password="querent",
#         host="localhost",
#         port="5432"
#     )
    
#     db_manager.connect_db()
#     db_manager.create_tables()
    
#     create_emb = EmbeddingStore()
    
#     # Set up the collectors
#     # directories = [ "/home/nishantg/querent-main/resp/Data/GOM Basin"]
#     # directories = [ "/home/nishantg/querent-main/querent/tests/data/llm/case_study_files"] 
#     # directories = ["/home/nishantg/querent-main/querent/tests/data/llm/predicate_checker"]
#     directories = ["/home/nishantg/querent-main/Demo_june 6/demo_files"]
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
#     # ner_model_name="English",
#     ner_model_name = "GeoBERT",
#     rel_model_type = "bert",
#     # rel_model_path = "/home/nishantg/Downloads/capybarahermes-2.5-mistral-7b.Q5_K_M.gguf",
#     rel_model_path = 'bert-base-uncased',
#     # rel_model_path = 'daryl149/llama-2-7b-chat-hf',
#     enable_filtering=True,
#     filter_params={
#             'score_threshold': 0.3,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.2,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.1
#         }
#     ,fixed_entities = [
#                     "Carbonate", "Clastic", "Porosity", "Permeability",
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
#                     "Economic analysis", "Market analysis", "oil well", "gas well", "well", "oil field", "gas field", "eagle ford", "ghawar", "johan sverdrup", "karachaganak","maracaibo"
#                 ]
#             , sample_entities = [
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
#                     "economic_aspect", "economic_aspect","hydrocarbon_source","hydrocarbon_source","hydrocarbon_source","hydrocarbon_source","hydrocarbon_source","reservoir","reservoir","reservoir","reservoir","reservoir"
#                 ]
#     # ,fixed_entities = [
#     #                 "Hadean", "Archean", "Proterozoic", "Phanerozoic",
#     #                 "Paleozoic", "Mesozoic", "Cenozoic",
#     #                 "Cambrian", "Ordovician", "Silurian", "Devonian", "Carboniferous", "Permian",
#     #                 "Triassic", "Jurassic", "Cretaceous",
#     #                 "Paleogene", "Neogene", "Quaternary",
#     #                 "Paleocene", "Eocene", "Oligocene",
#     #                 "Miocene", "Pliocene",
#     #                 "Pleistocene", "Holocene",
#     #                 "Anticline", "Syncline", "Fault", "Salt dome", "Horst", "Graben",
#     #                 "Reef", "Shoal", "Deltaic deposits", "Turbidite", "Channel sandstone",
#     #                 "Sandstone", "Limestone", "Dolomite", "Shale",
#     #                 "Source rock", "Cap rock",
#     #                 "Crude oil", "Natural gas", "Coalbed methane", "Tar sands", "Gas hydrates",
#     #                 "Structural trap", "Stratigraphic trap", "Combination trap", "Salt trap", "Unconformity trap",
#     #                 "Hydrocarbon migration", "Hydrocarbon accumulation",
#     #                 "Placer deposits", "Vein deposit", "Porphyry deposit", "Kimberlite pipe", "Laterite deposit",
#     #                 "Volcanic rock", "Basalt", "Geothermal gradient", "Sedimentology",
#     #                 "Paleontology", "Biostratigraphy", "Sequence stratigraphy", "Geophysical survey",
#     #                 "Magnetic anomaly", "Gravitational anomaly", "Petrology", "Geochemistry", "Hydrogeology", "trap"
#     #             ]

#     # , sample_entities=[
#     #                 "geological_eon", "geological_eon", "geological_eon", "geological_eon",
#     #                 "geological_era", "geological_era", "geological_era",
#     #                 "geological_period", "geological_period", "geological_period", "geological_period", "geological_period", "geological_period",
#     #                 "geological_period", "geological_period", "geological_period",
#     #                 "geological_period", "geological_period", "geological_period",
#     #                 "geological_epoch", "geological_epoch", "geological_epoch",
#     #                 "geological_epoch", "geological_epoch",
#     #                 "geological_epoch", "geological_epoch", "structural_feature", "structural_feature", "structural_feature", "structural_feature", "structural_feature", "structural_feature",
#     #                 "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature", "stratigraphic_feature",
#     #                 "rock_type", "rock_type", "rock_type", "rock_type",
#     #                 "rock_type", "rock_type", "hydrocarbon_source",
#     #                 "hydrocarbon", "hydrocarbon", "hydrocarbon", "hydrocarbon",
#     #                 "trap_type", "trap_type", "trap_type", "trap_type", "trap_type",
#     #                 "geological_process", "geological_process",
#     #                 "mineral_deposit", "mineral_deposit", "mineral_deposit", "mineral_deposit", "mineral_deposit",
#     #                 "rock_type", "rock_type", "geological_process", "geological_discipline",
#     #                 "geological_discipline", "geological_method", "geological_method", "geological_method",
#     #                 "geophysical_feature", "geophysical_feature", "geological_discipline", "geological_discipline", "geological_discipline", "trap_type"
#     #             ]
#     # ,fixed_entities = ["university", "greenwood", "liam zheng", "department", "Metroville", "Emily Stanton", "Coach", "health", "training", "atheletes" ]
#     # ,sample_entities=["organization", "organization", "person",  "department", "city", "person", "person", "method", "method", "person"]
#     ,is_confined_search = True
# #     fixed_relationships=[
# #     "Increase in research funding leads to environmental science focus",
# #     "Dr. Emily Stanton's advocacy for cleaner energy",
# #     "University's commitment to reduce carbon emissions",
# #     "Dr. Stanton's research influences architectural plans",
# #     "Collaborative project between sociology and environmental sciences",
# #     "Student government launches mental health awareness workshops",
# #     "Enhanced fitness programs improve sports teams' performance",
# #     "Coach Torres influences student-athletes' holistic health",
# #     "Partnership expands access to digital resources",
# #     "Interdisciplinary approach enriches academic experience"
# # ]
# #             , sample_relationships=[
# #     "Causal",
# #     "Contributory",
# #     "Causal",
# #     "Influential",
# #     "Collaborative",
# #     "Initiative",
# #     "Beneficial",
# #     "Influential",
# #     "Collaborative",
# #     "Enriching"
# # ] ,
            
        
#     ,user_context="Query: Your task is to analyze and interpret the context to construct semantic triples. The above context is from a  university document along with the identified entities using NER. Identify which entity is the subject entity and which is the object entity based on the context, and determine the meaningful relationship or predicate linking the subject entity to the object entity. Also identify the respective subject entity type , object entity and predicate type. Answer:"
#     )
#     llm_instance = BERTLLM(result_queue, bert_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
        
#         def average_embeddings(embedding1, embedding2, embedding3, embedding4, predicate_score):
#             emb1 = np.array(embedding1)
#             emb2 = np.array(embedding2)
#             emb3 = np.array(embedding3) * predicate_score
#             emb4 = np.array(embedding4)

#             # Calculate the average embedding
#             average_emb = (emb1 + emb2 + emb3 + emb4) / 4
#             return average_emb
        
#         import numpy as np

#         def weighted_average_embeddings(embeddings, weights=None, normalize_weights=True):
#             embeddings = [np.array(emb) for emb in embeddings]

#             if weights is None:
#                 weights = np.ones(len(embeddings))
#             else:
#                 weights = np.array(weights)
#                 if len(weights) != len(embeddings):
#                     raise ValueError("The number of weights must match the number of embeddings.")
#                 if normalize_weights:
#                     weights = weights / np.sum(weights)  # Normalize weights to sum to 1

#             weighted_sum = np.zeros_like(embeddings[0])
#             for emb, weight in zip(embeddings, weights):
#                 weighted_sum += emb * weight

#             return weighted_sum
        
#         def dynamic_weighted_average_embeddings(embeddings, base_weights, normalize_weights=True):
#             embeddings = [np.array(emb) for emb in embeddings]
#             weights = np.array(base_weights, dtype=float)

#             if normalize_weights:
#                 weights /= np.sum(weights)  # Normalize weights to sum to 1

#             weighted_sum = np.zeros_like(embeddings[0])
#             for emb, weight in zip(embeddings, weights):
#                 weighted_sum += emb * weight

#             return weighted_sum
        
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             if event_state['event_type'] == EventType.Graph:
#                 triple = json.loads(event_state['payload'])
#                 print("triple: {}".format(triple))
#                 assert isinstance(triple['subject'], str) and triple['subject']
#                 db_manager.insert_metadata(
#         subject=triple['subject'],
#         subject_type=triple['subject_type'],
#         predicate=triple['predicate'],
#         object=triple['object'],
#         object_type=triple['object_type'],
#         sentence=triple['sentence'],
#         file=event_state['file'],
#         doc_source=event_state['doc_source']
#     )          
#             elif event_state['event_type'] == EventType.Vector:
#                 triple_v = json.loads(event_state['payload'])
#                 # print("Vector Json :----: {}".format(triple_v))
#                 db_manager.insert_embedding(
#         document_source=event_state['doc_source'],
#         knowledge=triple_v['id'],
#         predicate=triple_v['namespace'],
#         sentence=triple_v['sentence'],
#         embeddings=triple_v['embeddings'],
#         file=event_state['file']
#     )
                 
                
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     llm_instance.subscribe(EventType.Vector, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )
#     querent_task = asyncio.create_task(querent.start())
#     await asyncio.gather(ingest_task, querent_task)
#     db_manager.close_connection()

# if __name__ == "__main__":

#     # Run the async function
#     asyncio.run(test_ingest_all_async())
    
