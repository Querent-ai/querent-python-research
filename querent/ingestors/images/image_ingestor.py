from typing import List, AsyncGenerator
import base64
import uuid
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_images import IngestedImages
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.processors.async_processor import AsyncProcessor
from querent.common.common_errors import (
    FileNotFoundError,
    IOError,
    UnidentifiedImageError,
)
import pytesseract
from PIL import Image, UnidentifiedImageError
import io
from querent.common.types.ingested_tokens import IngestedTokens
from querent.logging.logger import setup_logger


class ImageIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return ImageIngestor(processors)


class ImageIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.JPG)
        self.processors = processors
        self.logger = setup_logger(__name__, "ImageIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        try:
            current_file = None

            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue

                if chunk_bytes.file != current_file:
                    if current_file:
                        text = await self.extract_and_process_image(
                            CollectedBytes(file=current_file, data=collected_bytes)
                        )
                        if text is not None:
                            yield IngestedTokens(file=current_file, data=[text], error=None, doc_source=chunk_bytes.doc_source)
                            yield IngestedImages(file=current_file, image=str(base64.b64encode(collected_bytes)), image_name=f"{str(uuid.uuid4())}.{chunk_bytes.extension}", page_num=0, text=[], ocr_text=[text], doc_source=chunk_bytes.doc_source)
                            yield IngestedTokens(file=current_file, data=None, error=None, doc_source=chunk_bytes.doc_source)

                    current_file = chunk_bytes.file
                    collected_bytes = b""

                collected_bytes += chunk_bytes.data

            if current_file:
                text = await self.extract_and_process_image(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                if text is not None:
                    yield IngestedTokens(file=current_file, data=[text], error=None, doc_source=chunk_bytes.doc_source)
                    yield IngestedImages(file=current_file, image=str(base64.b64encode(collected_bytes)), image_name=f"{str(uuid.uuid4())}.{chunk_bytes.extension}", page_num=0, text=[], ocr_text=[text], doc_source=chunk_bytes.doc_source)
                    yield IngestedTokens(file=current_file, data=None, error=None, doc_source=chunk_bytes.doc_source)

        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}", doc_source=chunk_bytes.doc_source)

    async def extract_and_process_image(self, collected_bytes: CollectedBytes) -> str:
        text = await self.extract_text_from_image(collected_bytes)
        if not text:
            return
        return await self.process_data(text)

    async def extract_text_from_image(self, collected_bytes: CollectedBytes) -> str:
        try:
            image = Image.open(io.BytesIO(collected_bytes.data))
            image_status = await self.analyze_image(image)
            if not image_status:
                return

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Given file with name as {collected_bytes.file} not found"
            ) from exc
        except IOError as exc:
            raise IOError(
                f"Unable to open given file with name as {collected_bytes.file}"
            ) from exc
        except UnidentifiedImageError as exc:
            raise UnidentifiedImageError(
                f"Unable to open the given file with given name {collected_bytes.file}"
            ) from exc

        text = pytesseract.image_to_string(image)
        return str(text).encode("utf-8").decode("unicode_escape")

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
