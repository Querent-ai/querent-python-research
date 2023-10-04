from abc import ABC, abstractmethod
from typing import AsyncGenerator

from querent.common.types.collected_bytes import CollectedBytes


class Collector(ABC):
    @abstractmethod
    async def connect(self):
        raise NotImplementedError

    @abstractmethod
    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        raise NotImplementedError

    @abstractmethod
    async def disconnect(self):
        raise NotImplementedError
