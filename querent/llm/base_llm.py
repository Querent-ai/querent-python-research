from abc import ABC, abstractmethod
import asyncio
from typing import Any
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue


class BaseLLM(ABC):
    def __init__(
        self,
        input_queue: QuerentQueue[IngestedTokens],
        output_queue: QuerentQueue[Any],
        num_workers: int = 1,
    ):
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.num_workers = num_workers
        self.workers = []

    @abstractmethod
    async def process_tokens(self, data: IngestedTokens) -> Any:
        pass

    @abstractmethod
    def validate(self) -> bool:
        # Do some validation here because we don't want to start the worker if it's not going to work
        pass

    async def worker(self):
        try:
            if not self.validate():
                raise Exception("Validation failed for " + self.__class__.__name__)
            while True:
                data = await self.input_queue.get()
                if data is None:
                    # Sentinel value to stop the worker
                    break
                result = await self.process_tokens(data)
                await self.output_queue.put(result)
                self.input_queue.task_done()
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Worker error: {e}")

    async def start_workers(self, num_workers: int = 1):
        self.workers = [self.worker() for _ in range(num_workers)]
        return self.workers

    async def stop_workers(self):
        try:
            # Signal the workers to stop by putting None into the input queue
            for _ in range(self.num_workers):
                await self.input_queue.put(None)
            # Wait for the workers to finish processing
            await asyncio.gather(*self.workers)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"Stop workers error: {e}")
        finally:
            # Close the output queue
            await self.output_queue.close()
