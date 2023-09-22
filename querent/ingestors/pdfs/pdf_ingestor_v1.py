from typing import AsyncGenerator, List
import fitz  # PyMuPDF
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.common import common_errors


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

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[str, None]:
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
                    async for page_text in self.extract_and_process_pdf(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield page_text
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield ""
        finally:
            # process the last file
            try:
                async for page_text in self.extract_and_process_pdf(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield page_text
            except Exception as exc:
                yield ""

    async def extract_and_process_pdf(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        try:
            pdf = fitz.open(stream=collected_bytes.data, filetype="pdf")
        except fitz.DocumentError as exc:
            raise common_errors.DocumentError(
                f"Getting Document error on this file {collected_bytes.file}"
            ) from exc
        except TypeError as exc:
            raise common_errors.TypeError(
                f"Getting type error on this file {collected_bytes.file}"
            ) from exc
        for page in pdf:
            text = page.get_text()
            processed_text = await self.process_data(text)
            yield processed_text

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
