from typing import List, AsyncGenerator
import uuid
from PIL import Image
import pybase64
import pypdf
from querent.common import common_errors
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_images import IngestedImages
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.email.email_reader import EmailReader
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.logging.logger import setup_logger
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.ingested_tokens import IngestedTokens
import email
import pytesseract
from io import BytesIO
import io


class EmailIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"email", "eml"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return EmailIngestor(processors)


class EmailIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.TEXT)
        self.processors = processors
        self.logger = setup_logger(__name__, "EmailIngestor")
        self.email_reader = EmailReader()

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        collected_bytes = b""
        current_file = None
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for line in self.extract_and_process_email(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(
                            file=current_file,
                            data=[line],  # Wrap line in a list
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

            if current_file:
                async for line in self.extract_and_process_email(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield IngestedTokens(
                        file=current_file,
                        data=[line],  # Wrap line in a list
                        error=None,
                    )
                yield IngestedTokens(file=current_file, data=None, error=None)
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")

    async def extract_and_process_email(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        text = await self.extract_text_from_email(collected_bytes)
        processed_text = await self.process_data(text)
        lines = processed_text.split("\n")
        for line in lines:
            yield line

    async def extract_text_from_email(self, collected_bytes: CollectedBytes) -> str:
        text = ""
        try:
            msg = email.message_from_bytes(collected_bytes.data)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        body = part.get_payload(decode=True).decode()
                    except Exception as e:
                        self.logger.error(f"Error decoding attachment body: {e}")
                        continue

                    if (
                        content_type == "text/plain"
                        and "attachment" not in content_disposition
                    ):
                        return self.email_reader.clean_email_body(body)
                    elif "attachment" in content_disposition:
                        await self.handle_attachment(part, collected_bytes)
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    return self.email_reader.clean_email_body(body)
        except Exception as e:
            self.logger.error(f"Error extracting text from email: {e}")
        return text

    async def handle_attachment(self, attachment_part, collected_bytes: CollectedBytes):
        # Get attachment data and type
        attachment_data = attachment_part.get_payload(decode=True)
        attachment_type = attachment_part.get_content_type()

        # Check attachment type and handle accordingly
        if attachment_type.startswith("image/"):
            await self.handle_image_attachment(attachment_data, collected_bytes)
        elif attachment_type == "application/pdf":
            await self.handle_pdf_attachment(attachment_data, collected_bytes)
        else:
            # Handle other attachment types as needed
            self.logger.warning(f"Unsupported attachment type: {attachment_type}")

    async def handle_image_attachment(
        self, image_data, collected_bytes: CollectedBytes
    ):
        try:
            ocr_text = await self.get_ocr_from_image(image_data)
            processed_text = await self.process_data(ocr_text)
            yield IngestedImages(
                file=collected_bytes.file,
                image=pybase64.b64encode(image_data),
                image_name=uuid.uuid4(),
                page_num=None,
                text=None,
                coordinates=None,
                ocr_text=processed_text,
            )
        except Exception as e:
            self.logger.error(f"Error handling image attachment: {e}")

    async def handle_pdf_attachment(self, pdf_data, collected_bytes: CollectedBytes):
        try:
            async for page_text in self.extract_and_process_pdf(
                CollectedBytes(file=collected_bytes.file, data=pdf_data)
            ):
                yield IngestedTokens(
                    file=collected_bytes.file,
                    data=[page_text],
                    error=None,
                )
        except Exception as e:
            self.logger.error(f"Error handling PDF attachment: {e}")

    async def get_ocr_from_image(self, image):
        """Implement this to return ocr text of the image"""
        image = Image.open(io.BytesIO(image.data))
        text = pytesseract.image_to_string(image)
        return str(text).encode("utf-8").decode("unicode_escape")

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
            self.logger.error(f"Exception while extracting email {exc}")
            raise common_errors.TypeError(
                f"Getting type error on this file {collected_bytes.file}"
            ) from exc

        except Exception as exc:
            self.logger.error(f"Exception while extracting email {exc}")
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

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
