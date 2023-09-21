from typing import AsyncGenerator, List
from querent.common.types.collected_bytes import CollectedBytes
from querent.processors.async_processor import AsyncProcessor


class BaseIngestor:
    def __init__(self, processors: List[AsyncProcessor]):
        self.processors = processors

    async def process_data(self, text: str) -> List[str]:
        # Your common data processing logic here
        pass

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[str, None]:
        pass
