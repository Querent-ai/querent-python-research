from typing import List, AsyncGenerator
from bs4 import BeautifulSoup

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type


class HtmlIngestorFactory(IngestorFactory):
    """Ingestor factory for html files"""

    SUPPORTED_EXTENSIONS = {"html"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return HtmlIngestor(processors)


class HtmlIngestor(BaseIngestor):
    """Ingestor for html"""

    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.HTML)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        """Ingesting bytes of xml file"""
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    async for text in self.extract_and_process_html(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(file=current_file, data=text, error=None)
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            # process the last file
            async for text in self.extract_and_process_html(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=text, error=None)

    async def extract_and_process_html(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        """Function to extract and process xml files"""
        text = await self.extract_text_from_html(collected_bytes)
        processed_text = await self.process_data(text)
        yield processed_text

    async def extract_text_from_html(self, collected_bytes: CollectedBytes) -> str:
        """Function to extract text from xml"""
        html_content = collected_bytes.data.decode("UTF-8")
        soup = BeautifulSoup(html_content, "html.parser")
        text = []
        links = []
        tags = ["p", "h1", "h2", "h3", "h4", "h5", "a", "footer", "article"]
        for element in soup.find_all(tags):
            if element.name == "a":
                link_text = element.get_text().strip()
                link_href = element.get("href")
                links.append((link_text, link_href))
            else:
                element_text = element.get_text().strip()
                text.append(element_text)

        return text

    async def process_data(self, text: str) -> str:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
