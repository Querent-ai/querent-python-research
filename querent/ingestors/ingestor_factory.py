

from abc import ABC, abstractmethod
from typing import List, Optional
from querent.ingestors.base_ingestor import BaseIngestor

from querent.processors.async_processor import AsyncProcessor


class IngestorFactory(ABC):
    @abstractmethod
    async def supports(self, file_extension: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def create(self, file_extension: str, processors: List[AsyncProcessor]) -> BaseIngestor:
        raise NotImplementedError

class UnsupportedIngestor(IngestorFactory):
    def __init__(self, message: str):
        self.message = message

    async def supports(self, file_extension: str) -> bool:
        return False

    async def create(self, file_extension: str) -> Optional[BaseIngestor]:
        return None
