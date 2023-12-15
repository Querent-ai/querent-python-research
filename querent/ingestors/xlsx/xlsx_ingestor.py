from typing import List, AsyncGenerator
import io
import pandas as pd

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type
from querent.logging.logger import setup_logger


class XlsxIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"xlsx"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return XlsxIngestor(processors)


class XlsxIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.XLSX)
        self.processors = processors
        self.logger = setup_logger(__name__, "XlsxIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for data in self.extract_and_process_xlsx(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(
                            file=current_file,
                            data=[data],
                            error=None,
                        )
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            async for data in self.extract_and_process_xlsx(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(
                    file=current_file,
                    data=[data],
                    error=None,
                )
            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_xlsx(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[pd.DataFrame, None]:
        df = await self.extract_text_from_xlsx(collected_bytes)
        processed_text = await self.process_data(df.to_string())
        yield processed_text

    async def extract_text_from_xlsx(
        self, collected_bytes: CollectedBytes
    ) -> pd.DataFrame:
        excel_buffer = io.BytesIO(collected_bytes.data)
        dataframe = pd.read_excel(excel_buffer)
        return dataframe

    async def process_data(self, text: str) -> str:
        if self.processors is None or len(self.processors) == 0:
            return text
        try:
            processed_data = text
            for processor in self.processors:
                processed_data = await processor.process_text(processed_data)
            return processed_data
        except Exception as e:
            self.logger.error(f"Error while processing text: {e}")
