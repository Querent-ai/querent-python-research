# import asyncio
# import pytest
# from querent.common.types.querent_queue import QuerentQueue
# from querent.llm.transformers.gpt2_llm_v1 import GPT2LLM


# @pytest.mark.asyncio
# async def test_openai_llm():
#     # Create input and output queues
#     input_queue = QuerentQueue()
#     output_queue = QuerentQueue()

#     # Create an OpenAI LLM instance
#     llm = GPT2LLM(input_queue, output_queue)

#     # Start the LLM worker
#     worker = asyncio.create_task(llm.worker())

#     # Put some input data into the input queue
#     input_data = ["Hello, how are you?", "What is the weather today?"]
#     for data in input_data:
#         await input_queue.put(data)

#     # Signal the worker to stop by putting None into the input queue
#     await input_queue.close()

#     # Wait for the worker to finish processing
#     await worker

#     # Check the output queue for results and print them
#     results = []
#     async for result in output_queue:
#         results.append(result)
#     await output_queue.close()

#     # Assert that the results match the expected output
#     expected_output = [
#         "Some generated text based on input 1",
#         "Some generated text based on input 2",
#     ]
#     assert results == expected_output
