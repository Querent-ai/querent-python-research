import asyncio
import pytest
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.core.transformers.bert_llm_transformers import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent




@pytest.mark.asyncio
@pytest.mark.parametrize("input_data,model_name,llm_class,expected_entities", [
    (["Nishant is working from Delhi"], "dslim/bert-base-NER", BERTLLM, [("Nishant", "PER"), ("Delhi", "LOC")]),
    (["A rock is volcano and sedimentary"], "botryan96/GeoBERT", BERTLLM, [('volcano', 'GeoPetro'), ('sedimentary', 'GeoPetro')])
])
async def test_bertllm_ner_tokenization_and_entity_extraction(input_data, model_name, llm_class, expected_entities):
 # Create input queue and resource manager
    input_queue = QuerentQueue()
    resource_manager = ResourceManager()

    # Put the input data into the input queue
    ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
    await input_queue.put(ingested_data)
    
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data=None))
    

    # Create an instance of the provided LLM class
    llm_instance = llm_class(input_queue, model_name)


    # Define a callback function to subscribe to state changes

    async def state_change_callback(new_state):
        assert new_state.event_type == EventType.TOKEN_PROCESSED

    # Subscribe to state change events
    await llm_instance.subscribe(EventType.TOKEN_PROCESSED, state_change_callback)


    # Create a Querent instance with the LLM instance
    querent = Querent(
        [llm_instance],
        num_workers=1,
        resource_manager=resource_manager,
    )


    # Start the querent
    await querent.start()

    # Process the tokens and extract entities
    
    await llm_instance.process_tokens(ingested_data)
    
    
    # Validate the entity extraction
    entities = llm_instance._extract_entities_from_chunks(llm_instance._tokenize_and_chunk(ingested_data))
    
    for entity in expected_entities:
        assert entity in entities