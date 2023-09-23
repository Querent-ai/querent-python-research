from typing import AsyncGenerator, List
import fitz  # PyMuPDF
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
from querent.config.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor


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
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""

        async def process_and_yield(tokens):
            for page_text in tokens:
                yield page_text

        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    current_file = None
                    collected_bytes = b""
                    # report to metrics
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    yield process_and_yield(
                        self.extract_and_process_pdf(
                            CollectedBytes(file=current_file, data=collected_bytes)
                        )
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            # at the queue level, we can sample out the error
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            # process the last file
            yield process_and_yield(
                self.extract_and_process_pdf(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
            )

    async def extract_and_process_pdf(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedTokens, None]:
        pdf = fitz.open(stream=collected_bytes.data, filetype="pdf")
        for page in pdf:
            text = page.get_text()
            if not text:
                continue
            processed_text = await self.process_data(text)
            yield IngestedTokens(
                file=collected_bytes.file,
                data=processed_text,
                error=collected_bytes.error,
            )

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
