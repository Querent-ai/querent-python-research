from abc import ABC, abstractmethod

class AsyncProcessor(ABC):
    @abstractmethod
    async def process(self, data):
        pass
