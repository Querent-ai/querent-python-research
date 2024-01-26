# import asyncio
# import json
# import pytest
# from querent.callback.event_callback_interface import EventCallbackInterface
# from querent.common.types.querent_queue import QuerentQueue
# from querent.common.types.querent_event import EventState, EventType
# from querent.common.types.ingested_tokens import IngestedTokens
# from querent.common.types.querent_queue import QuerentQueue
# from querent.config.core.llm_config import LLM_Config
# from querent.core.transformers.bert_llm import BERTLLM
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent


# @pytest.mark.asyncio
# @pytest.mark.parametrize("input_data,ner_model_name, llm_class,expected_entities,filter_entities", [
#    (["In January 2024, Microsoft, headquartered in Redmond, Washington, announced a groundbreaking strategic partnership with SpaceX, Elon Musk's aerospace manufacturer and space transport services company based in Hawthorne, California, to enhance cloud computing capabilities in space, signaling a significant leap in satellite technology. The collaboration was unveiled at the International Technology Summit in Berlin, Germany, attended by industry leaders, including Sundar Pichai of Google and Tim Cook from Apple, alongside delegates from the European Space Agency (ESA) and NASA. Among the distinguished attendees was Dr. Angela Hayes, a renowned astrophysicist from Cambridge University in the UK, who emphasized the transformative potential of this partnership on astronomical research and global communication networks."],
# "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["tectonic perturbations","downstream sectors"], True)])



# async def test_mixtralllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, llm_class, expected_entities, filter_entities):
#     input_queue = QuerentQueue()
#     resource_manager = ResourceManager()
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
#     await input_queue.put(ingested_data)
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=None)
#     await input_queue.put(ingested_data)
#     await input_queue.put(None)
#     bert_llm_config = LLM_Config(
#         ner_model_name=ner_model_name,
#         rel_model_path="/home/nishantg/Downloads/openhermes-2.5-mistral-7b.Q5_K_M.gguf",
#         rel_model_type="mixtral",
#         user_context ="""
# Please analyze the provided context.
# Context: {context}
# Entity 1: {entity1} 
# Entity 2: {entity2}

# Query: First, using the semantic triple framework, determine which of the above entities is the subject and which is the object, and what is the predicate between these entities. The determine the subject type, object type, and predicate type.

# Answer:""",
#         enable_filtering=filter_entities,
#         filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.01,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#     )
#     llm_instance = llm_class(input_queue, bert_llm_config)
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