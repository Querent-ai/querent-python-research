import asyncio
import pytest
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_engine import BaseEngine
from querent.napper.querent import Querent
from querent.napper.resource_manager import ResourceManager

input_data = ["Data 1", "Data 2", "Data 3"]
input_queue = QuerentQueue()
output_queue = QuerentQueue()
resource_manager = ResourceManager()


# Define a simple mock LLM class for testing
class MockLLM(BaseEngine):
    async def process_tokens(self, data):
        return f"Processed: {data}"

    def validate(self):
        return True


@pytest.mark.asyncio
async def test_querent_with_base_llm():
    # Put some input data into the input queue
    input_data = ["Data 1", "Data 2", "Data 3", None]
    for data in input_data:
        await input_queue.put(data)
    # Wait for the tasks to finish processing (implicitly handled by Querent)
    num_llms = 1
    llms = [MockLLM(input_queue, output_queue) for _ in range(num_llms)]

    # Create a Querent instance
    querent = Querent(llms, num_workers=num_llms, resource_manager=resource_manager)

    # Start the querent

    await querent.start()

    # Check the output queue for results and store them in a list
    results = []
    async for result in output_queue:
        results.append(result)
        output_queue.task_done()

    # Assert that the results match the expected output
    expected_output = [
        "Processed: Data: ['Data 1']",
        "Processed: Data: ['Data 2']",
        "Processed: Data: ['Data 3]",
    ]
    assert len(results) == len(expected_output)
