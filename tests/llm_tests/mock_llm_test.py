import asyncio
import pytest
from querent.common.types.querent_event import EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_engine import BaseEngine
from querent.napper.querent import Querent
from querent.napper.resource_manager import ResourceManager

# Create input and output queues
input_queue = QuerentQueue()
resource_manager = ResourceManager()


# Define a simple mock LLM class for testing
class MockLLM(BaseEngine):
    async def process_tokens(self, data):
        if data is None:
            # the LLM developer can raise an error here or do something else
            # the developers of Querent can customize the behavior of Querent
            # to handle the error in a way that is appropriate for the use case
            raise ValueError("Received None, terminating")
        self.state = f"Processing: Data: '{data}'"

    def validate(self):
        return True

    def set_state(self, new_state):
        self.state = new_state

    async def get_state(self):
        return self.state


@pytest.mark.asyncio
async def test_querent_with_base_llm():
    # Put some input data into the input queue
    input_data = ["Data 1", "Data 2", "Data 3", None]
    for data in input_data:
        await input_queue.put(data)

    ### A Typical Use Case ###
    # Create an engine to harness the LLM
    llm_mocker = MockLLM(input_queue)

    # Define a callback function to subscribe to state changes
    def state_change_callback(new_state):
        assert new_state.startswith("Processing: Data:")

    # Subscribe to state change events
    # This pattern is ideal as we can expose multiple events for each use case of the LLM
    llm_mocker.subscribe(EventType._STATE_TRANSITION, state_change_callback)

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
    querent = Querent(
        [llm_mocker],
        num_workers=1,
        resource_manager=resource_manager,
    )

    # Start the querent
    await querent.start()
