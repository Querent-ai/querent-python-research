from typing import AsyncGenerator, List
import fitz  # PyMuPDF
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.ingestor_factory import Ingestor, IngestorFactory
from querent.processors.async_processor import AsyncProcessor


class PdfIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"pdf"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(self, file_extension: str, processors: List[AsyncProcessor]) -> Ingestor:
        if not self.supports(file_extension):
            return None
        return PdfIngestor(processors)


class PdfIngestor(Ingestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(Ingestor.PDF)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[List[str], None]:
        try:
            collected_bytes = b""  # Initialize an empty byte string
            current_file = None

            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue  # Skip error bytes

                # If it's a new file, start collecting bytes for it
                if chunk_bytes.file != current_file:
                    if current_file:
                        # Process the collected bytes of the previous file
                        text = await self.extract_and_process_pdf(
                            CollectedBytes(file=current_file, data=collected_bytes)
                        )
                        yield text
                    collected_bytes = b""  # Reset collected bytes for the new file
                    current_file = chunk_bytes.file

                collected_bytes += chunk_bytes.data  # Collect the bytes

            # Process the collected bytes of the last file
            if current_file:
                text = await self.extract_and_process_pdf(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                yield text

        except Exception as e:
            yield []

    async def extract_and_process_pdf(self, collected_bytes: CollectedBytes) -> List[str]:
        text = await self.extract_text_from_pdf(collected_bytes)
        return await self.process_data(text)

    async def extract_text_from_pdf(self, collected_bytes: CollectedBytes) -> str:
        pdf = fitz.open(stream=collected_bytes.data, filetype="pdf")
        text = ""
        for page in pdf:
            text += page.getText()
        return text

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
