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
import fitz
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
            loader = fitz.open(stream=path.read(), filetype="pdf")

            for page in loader:
                text = page.get_text()
                if not text:
                    continue

                text = text.replace('\"', ' ').replace('\“', '').replace('\”', '')

                processed_text = await self.process_data(text)
                # Yield processed text as IngestedTokens
                yield IngestedTokens(
                    file=collected_bytes.file,
                    data=processed_text,
                    error=collected_bytes.error,
                )
            
            async for imgae_data in self.extract_img(loader, collected_bytes.file, collected_bytes.data):
                yield imgae_data

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
        
    async def extract_img(self, doc, file_path, data):
        image_page_map = {}

        # Iterate through the pages to fill the map
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)  # Get full details including xref
            for img in image_list:
                xref = img[0]
                image_page_map[xref] = page_num + 1  # Page numbers are 1-indexed for humans

        # Now we can extract images knowing their page numbers
        for xref, page_num in image_page_map.items():
            img = doc.extract_image(xref)
            if img:  # If image extraction was successful
                image_data = img["image"]
                image_ext = img["ext"]
                ocr_text = await self.get_ocr_from_image(image=img["image"])

                # Adjust page_num for 0-indexed access and check if it's within range
                page_index = page_num - 1
                if page_index < len(doc):
                    text_content = doc[page_index].get_text()
                else:
                    text_content = "Page not in document."

                yield IngestedImages(
                    file=file_path,
                    image=pybase64.b64encode(data),
                    image_name=f"{str(uuid.UUID)}.{image_ext}",
                    page_num=page_num,
                    text=[text_content],
                    coordinates=None,
                    ocr_text=[ocr_text],
                )

    async def get_ocr_from_image(self, image):
        """Implement this to return ocr text of the image"""
        try:
            image = Image.open(io.BytesIO(image))
            text = pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.error("Exception-{e}")
            raise e
        return str(text).encode("utf-8").decode("utf-8")

    async def process_data(self, text: str) -> str:
        if self.processors is None or len(self.processors) == 0:
            return [text]
        try:
            processed_data = text
            for processor in self.processors:
                processed_data = await processor.process_text(processed_data)
            return [processed_data]
        except Exception as e:
            self.logger.error(f"Error while processing text: {e}")
