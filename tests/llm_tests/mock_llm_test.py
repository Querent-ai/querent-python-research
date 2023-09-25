import asyncio
import pytest
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_llm import BaseLLM
from querent.napper.querent import Querent
from querent.napper.resource_manager import ResourceManager


# Define a simple mock LLM class for testing
class MockLLM(BaseLLM):
    async def process_tokens(self, data):
        return f"Processed: {data}"

    def validate(self):
        return True


@pytest.mark.asyncio
async def test_querent_with_base_llm():
    # Create input and output queues
    input_queue = QuerentQueue()
    output_queue = QuerentQueue()

    # Create a list of mock LLM instances
    num_llms = 3
    llms = [MockLLM(input_queue, output_queue) for _ in range(num_llms)]

    # Create a Querent instance
    querent = Querent(llms, num_workers=num_llms, resource_manager=ResourceManager())

    # Put some input data into the input queue
    input_data = ["Data 1", "Data 2", "Data 3"]
    for data in input_data:
        await input_queue.put(data)

    # Start the Querent
    await querent.start()

    # Signal the Querent to stop by putting None into the input queue
    await input_queue.close()

    # Wait for the tasks to finish processing (implicitly handled by Querent)
    # No need to explicitly create tasks for MockLLM instances

    # Check the output queue for results and store them in a list
    results = []
    async for result in output_queue:
        results.append(result)
    await output_queue.close()

    # Assert that the results match the expected output
    expected_output = ["Processed: Data 1", "Processed: Data 2", "Processed: Data 3"]
    assert results == expected_output


# Run the test
if __name__ == "__main__":
    asyncio.run(test_querent_with_base_llm())
