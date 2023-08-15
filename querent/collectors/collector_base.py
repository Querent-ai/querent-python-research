from abc import ABC, abstractmethod
from typing import AsyncGenerator

from querent.collectors.collector_result import CollectorResult

class Collector(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        pass

    @abstractmethod
    async def disconnect(self):
        pass
