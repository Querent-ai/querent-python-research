"""Ingestor file for xml"""
from typing import List, AsyncGenerator
import xml.etree.ElementTree as ET
from io import BytesIO

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.config.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.common.types.collected_bytes import CollectedBytes


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

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[str, None]:
        """Ingesting bytes of xml file"""
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
                    async for text in self.extract_and_process_xml(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield text
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            # TODO handle exception
            yield ""
        finally:
            # process the last file
            async for text in self.extract_and_process_xml(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield text

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

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
