from abc import abstractmethod
from typing import AsyncGenerator, List
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
from querent.processors.async_processor import AsyncProcessor


class BaseIngestor:
    def __init__(self, processors: List[AsyncProcessor]):
        self.processors = processors

    @abstractmethod
    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        # Your common ingestion logic here
        raise NotImplementedError

    @abstractmethod
    async def process_data(self, text):
        # Your common data processing logic here
        raise NotImplementedError
