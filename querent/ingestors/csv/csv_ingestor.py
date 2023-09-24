from typing import List, AsyncGenerator
import csv
import io

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens


class CsvIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"csv"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not self.supports(file_extension):
            return None
        return CsvIngestor(processors)


class CsvIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.CSV)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    # TODO handle error
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    async for row in self.extract_and_process_csv(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(file=current_file, data=[row], error=None)
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            # process the last file
            async for row in self.extract_and_process_csv(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=[row], error=None)

    async def extract_and_process_csv(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        text = await self.extract_text_from_csv(collected_bytes)
        rows = text.splitlines()
        for row in rows:
            processed_row = await self.process_data(row)
            yield processed_row

    async def extract_text_from_csv(self, collected_bytes: CollectedBytes) -> str:
        text_data = collected_bytes.data.decode("utf-8")
        return text_data

    async def process_data(self, text: str) -> str:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
