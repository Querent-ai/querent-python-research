from typing import List, AsyncGenerator
import xml.etree.ElementTree as ET
from io import BytesIO

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type
from querent.logging.logger import setup_logger


class XmlIngestorFactory(IngestorFactory):
    """Ingestor factory for xlsx files"""

    SUPPORTED_EXTENSIONS = {"xml"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return XmlIngestor(processors)


class XmlIngestor(BaseIngestor):
    """Ingestor for xml"""

    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.XML)
        self.processors = processors
        self.logger = setup_logger(__name__, "XmlIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        """Ingesting bytes of xml file"""
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for text in self.extract_and_process_xml(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(file=current_file, data=[text], error=None)
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
            async for text in self.extract_and_process_xml(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=[text], error=None)

            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_xml(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        """Function to extract and process xml files"""
        text = await self.extract_text_from_xml(collected_bytes)
        processed_text = await self.process_data(text)
        yield processed_text

    async def extract_text_from_xml(self, collected_bytes: CollectedBytes) -> str:
        """Function to extract text from xml"""
        text = collected_bytes.data.decode("UTF-8")
        return text

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
