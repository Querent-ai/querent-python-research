from typing import List, AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor_config import IngestorBackend


class TextIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"txt"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not self.supports(file_extension):
            return None

        return TextIngestor(processors)


class TextIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        self.processors = processors
        super.__init__(IngestorBackend.TEXT)

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[List[str], None]:
        try:
            collected_bytes = b""
            current_file = None

            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue

                if chunk_bytes.file != current_file:
                    if current_file:
                        text = await self.extract_and_process_text(
                            CollectedBytes(file=current_file, data=collected_bytes)
                        )
                        yield text

                    collected_bytes = b""
                    current_file = chunk_bytes.file

                collected_bytes += chunk_bytes.data

            if current_file:
                text = await self.extract_and_process_text(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                yield text

        except Exception as e:
            yield []

    async def extract_and_process_text(
        self, collected_bytes: CollectedBytes
    ) -> List[str]:
        text = await self.extract_text_from_file(collected_bytes)
        return await self.process_data(text=text)

    async def extract_text_from_file(collected_bytes: CollectedBytes) -> str:
        text = collected_bytes.data.decode("utf-8")
        return text

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
