"""Ingestor file for html"""
from typing import List, AsyncGenerator
from bs4 import BeautifulSoup

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common import common_errors


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
                    async for text in self.extract_and_process_html(
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
            async for text in self.extract_and_process_html(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield text

    async def extract_and_process_html(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        """Function to extract and process xml files"""
        try:
            text = await self.extract_text_from_html(collected_bytes)
            processed_text = await self.process_data(text)
            yield processed_text
        except Exception as exc:
            yield ""

    async def extract_text_from_html(self, collected_bytes: CollectedBytes) -> str:
        """Function to extract text from xml"""
        text = []
        try:
            html_content = collected_bytes.data.decode("UTF-8")
            soup = BeautifulSoup(html_content, "html.parser")
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
            processed_data = await processor.process(processed_data)
        return processed_data
