import asyncio
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    def __init__(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    @abstractmethod
    async def process_data(self, data):
        pass

    async def worker(self):
        while True:
            data = await self.input_queue.get()
            if data is None:
                # Sentinel value to stop the worker
                break
            result = await self.process_data(data)
            await self.output_queue.put(result)

    def start(self, num_workers=1):
        workers = [self.worker() for _ in range(num_workers)]
        return workers

    async def stop(self, workers):
        for _ in workers:
            await self.input_queue.put(None)  # Send sentinel values to stop workers
        await asyncio.gather(*workers)  # Wait for workers to finish

    async def process(self):
        workers = self.start()
        await self.stop(workers)
