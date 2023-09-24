from typing import List, AsyncGenerator
from io import BytesIO
from pptx import Presentation
from tika import parser

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type


class PptIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"ppt", "pptx"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return PptIngestor(processors)


class PptIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.PPT)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for page_text in self.extract_and_process_ppt(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(
                            file=current_file, data=[page_text], error=None
                        )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            async for page_text in self.extract_and_process_ppt(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=[page_text], error=None)

    async def extract_and_process_ppt(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        text = await self.extract_text_from_ppt(collected_bytes)
        processed_text = await self.process_data(text)
        yield processed_text

    async def extract_text_from_ppt(self, collected_bytes: CollectedBytes) -> str:
        if collected_bytes.extension == "pptx":
            ppt_file = BytesIO(collected_bytes.data)
            presentation = Presentation(ppt_file)
            text = []

            for slide in presentation.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        text.append(shape.text)

            text = "\n".join(text)
            return text
        elif collected_bytes.extension == "ppt":
            parsed = parser.from_buffer(collected_bytes.data)
            extracted_text = parsed["content"]
            return extracted_text

    async def process_data(self, text: str) -> str:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
