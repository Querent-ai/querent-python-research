import io
import tempfile
from typing import List, AsyncGenerator
import os
from docx import Document
import pytextract
import base64
import pytesseract
import uuid
from PIL import Image
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_images import IngestedImages
from querent.logging.logger import setup_logger


class DocIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"doc", "docx"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return DocIngestor(processors)


class DocIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.DOC)
        self.processors = processors
        self.logger = setup_logger(__name__, "DocIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    # TODO handle error
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    async for ingested_data in self.extract_and_process_doc(
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
            async for ingested_data in self.extract_and_process_doc(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield ingested_data
            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_doc(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        async for paragraph in self.extract_text_from_doc(collected_bytes):            
            yield paragraph

    async def extract_text_from_doc(self, collected_bytes: CollectedBytes) -> str:
        # Determine file extension
        file_extension = collected_bytes.extension.lower()
        if file_extension == "docx":
            doc = Document(io.BytesIO(collected_bytes.data))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            text = await self.process_data(text)
            yield IngestedTokens(
                file=collected_bytes.file, data=text, error=None
            )

            i = 1
            for rel in doc.part.rels.values():
                if "image" in rel.reltype:
                    image = rel.target_part.blob 
                    ocr_text = await self.process_image(image)
                    encoded_image = base64.b64encode(image)
                    yield IngestedImages(file = collected_bytes.file, image = encoded_image.decode('utf-8'), image_name=str(uuid.uuid4()), page_num=i, text=text, ocr_text=ocr_text, error=None, coordinates=None)
                    i += 1

        elif file_extension == "doc":
            current_doc_text = await self.temp_extract_from(collected_bytes)
            yield IngestedTokens(
                file=collected_bytes.file, data=[current_doc_text], error=None
            )
        else:
            raise common_errors.UnknownError(
                f"Not a doc or docx file {collected_bytes.file}"
            )

    async def temp_extract_from(self, collected_bytes: CollectedBytes) -> str:
        suffix = "." + collected_bytes.extension
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(collected_bytes.data)

        temp_file_path = temp_file.name
        try:
            txt = pytextract.process(temp_file_path).decode("utf-8")
            return txt
        except RuntimeError as exc:
            raise common_errors.RuntimeError(
                f"Getting ExtractionError on this file {collected_bytes.file}"
            ) from exc
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
        except pytextract.exceptions.ShellError as exc:
            raise common_errors.ShellError(
                f"Getting ShellError on this file {collected_bytes.file}"
            ) from exc
        finally:
            os.remove(temp_file_path)

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

    async def process_image(self, image_blob):
        try:
            image_stream = io.BytesIO(image_blob)

            image = Image.open(image_stream)

            ocr_text = pytesseract.image_to_string(image)

            return ocr_text
        except Exception as e:
            self.logger.error(f"Error during image processing: {e}")
            return ""