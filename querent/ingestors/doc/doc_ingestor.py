import io
import tempfile
from typing import List, AsyncGenerator
import os
from docx import Document
from docx2txt import process
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens
import pytextract


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
                    async for paragraph in self.extract_and_process_doc(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(
                            file=current_file, data=[paragraph], error=None
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
            # process the last file
            async for paragraph in self.extract_and_process_doc(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=[paragraph], error=None)
            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_doc(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        text = await self.extract_text_from_doc(collected_bytes)
        paragraphs = text.split("\n\n")  # Split by paragraphs
        for paragraph in paragraphs:
            processed_data = await self.process_data(paragraph)
            yield processed_data

    async def extract_text_from_doc(self, collected_bytes: CollectedBytes) -> str:
        # Determine file extension
        file_extension = collected_bytes.extension.lower()
        if file_extension == "docx":
            # For DOCX files, use python-docx library
            doc = Document(io.BytesIO(collected_bytes.data))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        elif file_extension == "doc":
            # For DOC files, use pyextract library
            current_doc_text = await self.temp_extract_from(collected_bytes)
            return current_doc_text
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
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
