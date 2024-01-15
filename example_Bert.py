import uuid
from pathlib import Path
import asyncio

from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.config.core.bert_llm_config import BERTLLMConfig
from querent.core.base_engine import BaseEngine
from querent.core.transformers.bert_llm import BERTLLM
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.config.collector.collector_config import FSCollectorConfig
from querent.ingestors.ingestor_manager import IngestorFactoryManager


async def main():
    # Initialize some collectors to collect the data
    directory_path = "./tests/data/llm/pdf"
    collectors = [
        CollectorResolver().resolve(
            Uri("file://" + str(Path(directory_path).resolve())),
            FSCollectorConfig(root_path=directory_path, id=str(uuid.uuid4())),
        )
    ]

    # Connect to the collector
    for collector in collectors:
        await collector.connect()

    # Set up the result queue
    result_queue = asyncio.Queue()

    # Create the IngestorFactoryManager
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    # Start the ingest_all_async in a separate task
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    ### A Typical Use Case ###
    # Create an engine to harness the LLM
    bert_llm_config = BERTLLMConfig(
    ner_model_name="botryan96/GeoBERT",
    enable_filtering=True,
    filter_params={
            'score_threshold': 0.5,
            'attention_score_threshold': 0.1,
            'similarity_threshold': 0.5,
            'min_cluster_size': 5,
            'min_samples': 3,
            'cluster_persistence_threshold':0.1
        }
    )
    llm_instance = BERTLLM(result_queue, bert_llm_config)

    # Define a callback function to subscribe to state changes
    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            print(f"New state: {event_state}")
            print(f"New state type: {event_type}")
            assert event_state.event_type == EventType.Graph

    # Subscribe to state change events
    # This pattern is ideal as we can expose multiple events for each use case of the LLM
    llm_instance.subscribe(EventType.Graph, StateChangeCallback())

    ## one can also subscribe to other events, e.g. EventType.CHAT_COMPLETION ...

    # Create a Querent instance with a single MockLLM
    # here we see the simplicity of the Querent
    # massive complexity is hidden in the Querent,
    # while being highly configurable, extensible, and scalable
    # async architecture helps to scale to multiple querenters
    # How async architecture works:
    #   1. Querent starts a worker task for each querenter
    #   2. Querenter starts a worker task for each worker
    #   3. Each worker task runs in a loop, waiting for input data
    #   4. When input data is received, the worker task processes the data
    #   5. The worker task notifies subscribers of state changes
    #   6. The worker task repeats steps 3-5 until termination
    termination_event = asyncio.Event()
    querent = Querent(
        [llm_instance],
        termination_event,
    )
    # Start the querent
    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)


asyncio.run(main())