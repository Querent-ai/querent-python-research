import asyncio
from abc import ABC, abstractmethod

from querent.common.types.querent_queue import QuerentQueue


class BaseLLM(ABC):
    def __init__(self, input_queue: QuerentQueue, output_queue: QuerentQueue):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.workers = []

    @abstractmethod
    async def process_data(self, data):
        pass

    @abstractmethod
    def validate(self):
        # Do some validation here because we don't want to start the worker if it's not going to work
        pass

    async def worker(self):
        try:
            if not self.validate():
                raise Exception("Validation failed for" + self.__class__.__name__)
            while True:
                data = await self.input_queue.get()
                if data is None:
                    # Sentinel value to stop the worker
                    break
                result = await self.process_data(data)
                await self.output_queue.put(result)
                self.input_queue.task_done()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Worker error: {e}")

    def start(self, num_workers=1):
        self.workers = [self.worker() for _ in range(num_workers)]
        return self.workers

    async def stop(self):
        for _ in self.workers:
            await self.input_queue.put(None)  # Send sentinel values to stop workers
        await asyncio.gather(
            *self.workers, return_exceptions=True
        )  # Wait for workers to finish

    async def process(self):
        try:
            await self.input_queue.join()  # Wait for all tasks to be processed
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Processing error: {e}")
