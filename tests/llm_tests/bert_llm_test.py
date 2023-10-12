import asyncio
import pytest
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.core.transformers.bert_llm_transformer import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent



@pytest.mark.asyncio
@pytest.mark.parametrize("input_data,ner_model_name,rel_model_name,llm_class,expected_entities", [
    ("Nishant is working from Delhi. Ansh is working from Punjab.", "dslim/bert-base-NER", "deepset/roberta-base-squad2", BERTLLM, [("Nishant", "PER"), ("Delhi", "LOC")]),
    ("A rock is volcano and sedimentary.", "botryan96/GeoBERT", "deepset/roberta-base-squad2", BERTLLM, [('volcano', 'GeoPetro'), ('sedimentary', 'GeoPetro')])])



async def test_bertllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, rel_model_name,  llm_class, expected_entities):
    """
        Test the BERTLLM class for NER tokenization and entity extraction.

        This test function evaluates the ability of the BERTLLM class to tokenize input data and extract named entities 
        using specified NER and Relationship models. The test ensures that the extracted entities match the expected 
        entities provided in the test parameters.

        Parameters:
            input_data (str): The input text data for tokenization and entity extraction.
            ner_model_name (str): The name of the NER model to be used for entity extraction.
            rel_model_name (str): The name of the Relationship model to be used.
            llm_class (class): The LLM class to be instantiated and tested.
            expected_entities (List[Tuple[str, str]]): A list of expected entities in the format (entity, entity_type).

        Assertions:
            - Asserts that the extracted entities match the expected entities.
            - Asserts that the event type is TOKEN_PROCESSED during state changes.
        """

    input_queue = QuerentQueue()
    resource_manager = ResourceManager()

    ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
    await input_queue.put(ingested_data)
    await input_queue.put(IngestedTokens(file="dummy_1_file.txt", data="Puneet is working from Houston."))
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data="dummy"))
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data=None, error="error"))
    
    llm_instance = llm_class(input_queue, ner_model_name, rel_model_name)

    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            print(f"New state: {event_state}")
            print(f"New state type: {event_type}")
            assert event_state.event_type == EventType.TOKEN_PROCESSED


    llm_instance.subscribe(EventType.TOKEN_PROCESSED, StateChangeCallback())

    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    entities = llm_instance._extract_entities_from_chunks(llm_instance._tokenize_and_chunk(ingested_data.data))
    
    for entity in expected_entities:
        assert entity in entities

    await querent.start()

