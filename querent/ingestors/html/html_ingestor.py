from typing import List, AsyncGenerator
from bs4 import BeautifulSoup
import io
import base64
from PIL import Image
import pytesseract
import uuid

from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_images import IngestedImages
from querent.logging.logger import setup_logger


class HtmlIngestorFactory(IngestorFactory):
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
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.HTML)
        self.processors = processors
        self.logger = setup_logger(__name__, "HtmlIngestor")

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
                    # we have a new file, process the old one
                    async for ingested_data in self.extract_and_process_html(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield ingested_data
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
            # process the last file
            async for ingested_data in self.extract_and_process_html(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield ingested_data
            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_html(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        """Function to extract and process xml files"""
        async for elements in self.extract_text_from_html(collected_bytes):
            yield elements

    async def extract_text_from_html(
        self, collected_bytes: CollectedBytes
    ) -> List[str]:
        """Function to extract text from xml"""
        try:
            html_content = collected_bytes.data.decode("UTF-8")
            soup = BeautifulSoup(html_content, "html.parser")
            elements = []
            tags = ["p", "h1", "h2", "h3", "h4", "h5", "a", "footer", "article"]
            for element in soup.find_all(tags):
                if element.name == "a":
                    link_text = element.get_text().strip()
                    link_href = element.get("href")
                    elements.append(f"Link: {link_text}, URL: {link_href}")
                else:
                    element_text = element.get_text().strip()
                    elements.append(element_text)

            i = 1
            for img_tag in soup.find_all('img'):
                img_src = img_tag.get('src')
                if img_src and img_src.startswith('data:image'):
                    base64_data = img_src.split(';base64,')[-1]
                    image_data = base64.b64decode(base64_data)
                    image_ocr = await self.process_image(io.BytesIO(image_data))

                    yield IngestedImages(file = collected_bytes.file, image = base64_data, image_name = str(uuid.uuid4()), page_num=i, text = soup, ocr_text = image_ocr, coordinates= None, error= None)
                    i += 1
        except UnicodeDecodeError as exc:
            raise common_errors.UnicodeDecodeError(
                f"Getting UnicodeDecodeError on this file {collected_bytes.file} as {exc}"
            ) from exc
        except LookupError as exc:
            raise common_errors.LookupError(
                f"Getting LookupError on this file {collected_bytes.file} as {exc}"
            ) from exc
        except TypeError as exc:
            raise common_errors.TypeError(
                f"Getting TypeError on this file {collected_bytes.file} as {exc}"
            ) from exc
        for element in elements:
            processed_element = await self.process_data(element)
            yield IngestedTokens(file=collected_bytes.file, data=[processed_element], error=None)

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

    async def process_image(self, image_stream):
        try:
            image = Image.open(image_stream)
            ocr_text = pytesseract.image_to_string(image)
            return ocr_text
        except Exception as e:
            self.logger.error(f"Error during image processing: {e}")
            return ""
