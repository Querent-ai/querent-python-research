from abc import ABC, abstractmethod
from typing import AsyncGenerator

from querent.common.types.collected_bytes import CollectedBytes


class Collector(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        pass

    @abstractmethod
    async def disconnect(self):
        pass
