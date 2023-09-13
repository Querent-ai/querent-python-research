"""Ingestor file for xlsx files"""
from typing import List, AsyncGenerator
import io
import openpyxl
import pandas as pd

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes


class XlsxIngestorFactory(IngestorFactory):
    """Ingestor factory for xlsx files"""

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
    """Ingestor for xlsx files"""

    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.XLSX)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[str, None]:
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
                    async for frames in self.extract_and_process_xlsx(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield frames
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            # TODO handle exception
            yield ""
        finally:
            # process the last file
            async for frames in self.extract_and_process_xlsx(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield frames

    async def extract_and_process_xlsx(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        """function to extract and process xlsx file bytes"""
        df = await self.extract_text_from_xlsx(collected_bytes)
        yield df

    async def extract_text_from_xlsx(
        self, collected_bytes: CollectedBytes
    ) -> pd.DataFrame:
        """function to extract all the rows in the file"""
        excel_buffer = io.BytesIO(collected_bytes.data)
        dataframe = pd.read_excel(excel_buffer)
        return dataframe

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
