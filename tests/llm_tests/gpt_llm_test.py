# import asyncio
# import json
# import pytest
# from querent.callback.event_callback_interface import EventCallbackInterface
# from querent.common.types.querent_queue import QuerentQueue
# from querent.common.types.querent_event import EventState, EventType
# from querent.common.types.ingested_tokens import IngestedTokens
# from querent.common.types.querent_queue import QuerentQueue
# from querent.config.core.gpt_llm_config import GPTConfig
# from querent.core.transformers.gpt_llm_bert_ner_or_fixed_entities_set_ner import GPTLLM
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent


# @pytest.mark.asyncio
# @pytest.mark.parametrize("input_data,ner_model_name, llm_class,expected_entities,filter_entities", [
#      (["In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe."],
# "botryan96/GeoBERT", GPTLLM, ["tectonic perturbations","downstream sectors"], True)])



# async def test_gptllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, llm_class, expected_entities, filter_entities):
#     input_queue = QuerentQueue()
#     resource_manager = ResourceManager()
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
#     await input_queue.put(ingested_data)
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=None)
#     await input_queue.put(ingested_data)
#     await input_queue.put(None)
#     gpt_llm_config = GPTConfig(
#         ner_model_name=ner_model_name,
#         enable_filtering=filter_entities,
#         filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#     )
#     print("going to initialize class")
#     llm_instance = llm_class(input_queue, gpt_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         def handle_event(self, event_type: EventType, event_state: EventState):
#             assert event_state.event_type == EventType.Graph
#             triple = json.loads(event_state.payload)
#             print("triple: {}".format(triple))
#             assert isinstance(triple['subject'], str) and triple['subject']
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )

#     await querent.start()

