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
        super().__init__(IngestorBackend.Email)
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
                    email = await self.extract_and_process_email(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    )
                    yield IngestedTokens(
                        file=current_file,
                        data=email,  # Wrap line in a list
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
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            if current_file is not None:
                email = await self.extract_and_process_email(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                yield IngestedTokens(
                    file=current_file,
                    data=email,  # Wrap line in a list
                    error=None,
                )
                yield IngestedTokens(
                    file=current_file,
                    data=None,
                    error=None,
                )

    async def extract_and_process_email(
        self, collected_bytes: CollectedBytes
    ) -> List[str]:
        text = await self.extract_text_from_email(collected_bytes)
        processed_text = await self.process_data(text)
        return processed_text

    async def extract_text_from_email(self, collected_bytes: CollectedBytes) -> str:
        text = ""
        try:
            msg = email.message_from_bytes(collected_bytes.data)
            email_msg = {}
            (
                email_msg["From"],
                email_msg["To"],
                email_msg["Date"],
                email_msg["Subject"],
            ) = self.email_reader.obtain_header(msg)
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    try:
                        body = part.get_payload(decode=True)
                    except Exception as e:
                        continue
                    if body is None:
                        continue
                    text += await self.handle_sub_part(part)
                    text += "\n"
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    text = self.email_reader.clean_email_body(body)
        except Exception as e:
            self.logger.error(f"Error extracting text from email: {e}")
        return text

    async def handle_sub_part(self, sub_part):
        sub_content_type = sub_part.get_content_type()
        sub_content_disposition = str(sub_part.get("Content-Disposition"))
        if (
            sub_content_type == "text/plain"
            and "attachment" not in sub_content_disposition
        ):
            return self.email_reader.clean_email_body(sub_part.get_payload())
        elif "attachment" in sub_content_disposition:
            # Handle attachment as needed
            return await self.handle_attachment(sub_part)
        elif sub_content_type == "text/html":
            # Handle HTML content as needed
            # You can choose to ignore or process it
            return ""
        else:
            # Handle other content types as needed
            return ""

    async def handle_attachment(self, attachment_part) -> str:
        # Get attachment data and type
        attachment_data = attachment_part.get_payload(decode=True)
        attachment_type = attachment_part.get_content_type()

        # Check attachment type and handle accordingly
        if attachment_type.startswith("image/"):
            return await self.handle_image_attachment(attachment_data)
        elif attachment_type == "application/pdf":
            return await self.handle_pdf_attachment(attachment_data)
        else:
            # Handle other attachment types as needed
            self.logger.warning(f"Unsupported attachment type: {attachment_type}")

    async def handle_image_attachment(self, image_data: bytes) -> str:
        try:
            ocr_text = await self.get_ocr_from_image(image_data)
            return ocr_text
        except Exception as e:
            self.logger.error(f"Error handling image attachment: {e}")

    async def handle_pdf_attachment(self, pdf_data) -> str:
        try:
            pdf_text = await self.extract_and_process_pdf(pdf_data)
        except Exception as e:
            self.logger.error(f"Error handling PDF attachment: {e}")
        return pdf_text

    async def get_ocr_from_image(self, image):
        """Implement this to return ocr text of the image"""
        image = Image.open(io.BytesIO(image))
        text = pytesseract.image_to_string(image)
        return str(text).encode("utf-8").decode("unicode_escape")

    async def extract_and_process_pdf(self, pdf_data: bytes) -> str:
        pdf_text = ""
        try:
            path = BytesIO(pdf_data)
            loader = pypdf.PdfReader(path)

            for _, page in enumerate(loader.pages):
                text = page.extract_text()
                pdf_text += text + "\n"
                pdf_text += await self.extract_images_and_ocr(page)

        except TypeError as exc:
            self.logger.error(f"Exception while extracting email {exc}")
        except Exception as exc:
            self.logger.error(f"Exception while extracting email {exc}")
        return pdf_text

    async def extract_images_and_ocr(self, page) -> str:
        ocr_text = ""
        try:
            for image_path in page.images:
                ocr_text += await self.get_ocr_from_image(image_path)
        except Exception as e:
            self.logger.error(f"Error extracting images and OCR: {e}")
        return ocr_text

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
