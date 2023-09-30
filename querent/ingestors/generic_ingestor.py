from typing import List, AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor_config import IngestorBackend
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens


class GenericIngestorFactory(IngestorFactory):
    async def supports(self, file_extension: str) -> bool:
        return file_extension == "" or file_extension is None

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return GenericIngestor(processors)


class GenericIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.TEXT)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        collected_bytes = b""
        current_file = None
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue
                collected_bytes += chunk_bytes.data

            async for line in self.extract_and_process_text(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(
                    file=None,
                    data=[line],
                    error=None,
                )
        except Exception as exc:
            raise common_errors.UnknownError(
                f"Received error as {exc} from Generic Ingestor"
            ) from exc

    async def extract_and_process_text(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        text = await self.extract_text_from_bytes(collected_bytes)
        processed_text = await self.process_data(text)
        lines = processed_text.split("\n")
        for line in lines:
            yield line

    async def extract_text_from_bytes(self, collected_bytes: CollectedBytes) -> str:
        text = ""
        try:
            text = collected_bytes.data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise common_errors.UnicodeDecodeError(
                f"Getting UnicodeDecodeError on this file {collected_bytes.file}"
            ) from exc
        except LookupError as exc:
            raise common_errors.LookupError(
                f"Getting LookupError on this file {collected_bytes.file}"
            ) from exc
        except TypeError as exc:
            raise common_errors.TypeError(
                f"Getting TypeError on this file {collected_bytes.file}"
            ) from exc
        return text

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
