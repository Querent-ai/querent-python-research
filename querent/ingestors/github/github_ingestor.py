from typing import List, AsyncGenerator

from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.collected_bytes import CollectedBytes


class GithubIngestor(BaseIngestor):
    """Class for ingesting github code"""

    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.GITHUB)
        self.processorrs = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedCode, None]:
        collected_bytes = b""
        current_file = None
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for line in self.extract_and_process_code(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedCode(
                            file=current_file,
                            data=[line],  # Wrap line in a list
                            error=None,
                        )
                    yield IngestedCode(
                        file=current_file,
                        data=None,
                        error=None,
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file

                collected_bytes += chunk_bytes.data

            if current_file:
                async for line in self.extract_and_process_code(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield IngestedCode(
                        file=current_file,
                        data=[line],  # Wrap line in a list
                        error=None,
                    )
                yield IngestedCode(file=current_file, data=None, error=None)
        except Exception as e:
            yield IngestedCode(file=current_file, data=None, error=f"Exception: {e}")

    async def extract_and_process_code(
        self, chunk_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedCode, None]:
        message_bytes = chunk_bytes.data.decode("UTF-8")
        yield message_bytes


class GithubIngestorFactory(IngestorFactory):
    """Class for github ingestor factory"""

    SUPPORTED_EXTENSIONS = {"github"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return GithubIngestor(processors)
