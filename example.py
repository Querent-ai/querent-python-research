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
from querent.core.base_engine import BaseEngine
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.config.collector.collector_config import FSCollectorConfig
from querent.ingestors.ingestor_manager import IngestorFactoryManager

# Create input and output queues

# Define a simple mock LLM engine for testing
class MockLLMEngine(BaseEngine):
    def __init__(self, input_queue: QuerentQueue):
        super().__init__(input_queue)

    async def process_tokens(self, data: IngestedTokens):
        if data is None or data.is_error():
            # the LLM developer can raise an error here or do something else
            # the developers of Querent can customize the behavior of Querent
            # to handle the error in a way that is appropriate for the use case
            self.set_termination_event()
            return
        # Set the state of the LLM
        # At any given point during the execution of the LLM, the LLM developer
        # can set the state of the LLM using the set_state method
        # The state of the LLM is stored in the state attribute of the LLM
        # The state of the LLM is published to subscribers of the LLM
        current_state = EventState(EventType.Graph, 1.0, "anything", "dummy.txt")
        await self.set_state(new_state=current_state)

    async def process_code(self, data: IngestedCode):
        pass

    async def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    async def process_images(self, data: IngestedImages):
        return super().process_images(data)

    def validate(self):
        return True


async def main():
    # Initialize some collectors to collect the data
    directory_path = "./tests/data/pdf4"
    uri = Uri("file://" + str(Path(directory_path).resolve()))
    collectors = [
        CollectorResolver().resolve(
            uri=uri,
            config = FSCollectorConfig(config_source={
            "id": str(uuid.uuid4()),
            "root_path": uri.path,
            "name": "Local-config",
            "config": {},
            "uri": "file://",
        }),
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
    llm_mocker = MockLLMEngine(result_queue)

    # Define a callback function to subscribe to state changes
    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            print(f"New state: {event_state}")
            print(f"New state type: {event_type}")
            assert event_state.event_type == EventType.Graph

    # Subscribe to state change events
    # This pattern is ideal as we can expose multiple events for each use case of the LLM
    llm_mocker.subscribe(EventType.Graph, StateChangeCallback())

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
    resource_manager = ResourceManager()
    querent = Querent(
        [llm_mocker],
        resource_manager=resource_manager,
    )
    # Start the querent
    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)


asyncio.run(main())