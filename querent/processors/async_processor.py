from abc import ABC, abstractmethod


class AsyncProcessor(ABC):
    @abstractmethod
    async def process_text(self, data: str) -> str:
        raise NotImplementedError
