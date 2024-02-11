from typing import AsyncGenerator, List
from io import BytesIO
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_images import IngestedImages
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.logging.logger import setup_logger
from querent.processors.async_processor import AsyncProcessor
from querent.common import common_errors
import uuid
import pypdf
from PIL import Image
import io

import pybase64
import pytesseract


class PdfIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"pdf"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return PdfIngestor(processors)


class PdfIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.PDF)
        self.processors = processors
        self.logger = setup_logger(__name__, "PdfIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens or str, None]: # type: ignore
        current_file = None
        collected_bytes = b""

        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    # report to metrics
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    async for page_text in self.extract_and_process_pdf(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield page_text
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                    )
                collected_bytes += chunk_bytes.data
        except Exception as e:
            # at the queue level, we can sample out the error
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            # process the last file
            try:
                async for page_text in self.extract_and_process_pdf(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield page_text

                yield IngestedTokens(file=current_file, data=None, error=None)
            except Exception as exc:
                yield IngestedTokens(
                    file=current_file,
                    data=None,
                    error=f"Exception: {exc}",
                )

    async def extract_and_process_pdf(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedTokens, None]:
        try:
            path = BytesIO(collected_bytes.data)
            loader = pypdf.PdfReader(path)

            for page_num, page in enumerate(loader.pages):
                text = page.extract_text()
                if not text:
                    continue

                processed_text = await self.process_data(text)

                # Yield processed text as IngestedTokens
                yield IngestedTokens(
                    file=collected_bytes.file,
                    data=processed_text,
                    error=collected_bytes.error,
                )
                async for image_result in self.extract_images_and_ocr(
                    page,
                    page_num,
                    processed_text,
                    collected_bytes.data,
                    collected_bytes.file,
                ):
                    yield image_result

        except TypeError as exc:
            self.logger.error(f"Exception while extracting pdf {exc}")
            raise common_errors.TypeError(
                f"Getting type error on this file {collected_bytes.file}"
            ) from exc

        except Exception as exc:
            self.logger.error(f"Exception while extracting pdf {exc}")
            raise common_errors.UnknownError(
                f"Getting unknown error while handling this file: {collected_bytes.file} error - {exc}"
            ) from exc

    async def extract_images_and_ocr(self, page, page_num, text, data, file_path):
        try:
            for image_path in page.images:
                ocr = await self.get_ocr_from_image(image_path)
                yield IngestedImages(
                    file=file_path,
                    image=pybase64.b64encode(data),
                    image_name=uuid.uuid4(),
                    page_num=page_num,
                    text=text,
                    coordinates=None,
                    ocr_text=ocr,
                )
        except Exception as e:
            self.logger.error(f"Error extracting images and OCR: {e}")
            yield IngestedImages(
                file=file_path,
                image=pybase64.b64encode(data),
                image_name=uuid.uuid4(),
                page_num=page_num,
                text=text,
                coordinates=None,
                ocr_text=None,
                error=f"Exception:{e}",
            )

    async def get_ocr_from_image(self, image):
        """Implement this to return ocr text of the image"""
        try:
            image = Image.open(io.BytesIO(image.data))
            text = pytesseract.image_to_string(image)
        except Exception as e:
            print("Exception-{e}")
        return str(text).encode("utf-8").decode("unicode_escape")

    async def process_data(self, text: str) -> str:
        if self.processors is None or len(self.processors) == 0:
            return [text]
        try:
            processed_data = text
            for processor in self.processors:
                processed_data = await processor.process_text(processed_data)
            return processed_data
        except Exception as e:
            self.logger.error(f"Error while processing text: {e}")
