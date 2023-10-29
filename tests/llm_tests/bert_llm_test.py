import asyncio
import pytest
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.core.transformers.bert_llm import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent


@pytest.mark.asyncio
@pytest.mark.parametrize("input_data,ner_model_name, llm_class,expected_entities", [
    ("Nishant is working from Delhi. Ansh is working from Punjab.", "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["http://geodata.org/Nishant", "http://geodata.org/Delhi"]),
    ("In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.","botryan96/GeoBERT", BERTLLM, ["http://geodata.org/eocene","http://geodata.org/mexico"])])



async def test_bertllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, llm_class, expected_entities):
    input_queue = QuerentQueue()
    resource_manager = ResourceManager()
    
    
    ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
    await input_queue.put(ingested_data)
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data="dummy"))
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data=None, error="error"))
    
    llm_instance = llm_class(input_queue, ner_model_name)

    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            assert event_state.event_type == EventType.TOKEN_PROCESSED
            # Accessing the data (triples) from the event_state
            triples = event_state.payload

            # Extracting subjects and objects from the triples
            subjects = [triple[0].value for triple in triples]
            objects = [triple[2].value for triple in triples]

            assert expected_entities[0] in subjects
            assert expected_entities[1] in objects


    llm_instance.subscribe(EventType.TOKEN_PROCESSED, StateChangeCallback())

    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    await querent.start()

