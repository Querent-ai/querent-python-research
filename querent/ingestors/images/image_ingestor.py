from typing import List, AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor_config import IngestorBackend
import pytesseract
from PIL import Image
import io
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type


class ImageIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not self.supports(file_extension):
            return None
        return ImageIngestor(processors)


class ImageIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.JPG)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        try:
            collected_bytes = b""
            current_file = None

            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
                    continue

                if chunk_bytes.file != current_file:
                    if current_file:
                        text = await self.extract_and_process_image(
                            CollectedBytes(file=current_file, data=collected_bytes)
                        )
                        yield IngestedTokens(file=current_file, data=text, error=None)
                    collected_bytes = b""
                    current_file = chunk_bytes.file

                collected_bytes += chunk_bytes.data

            if current_file:
                text = await self.extract_and_process_image(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                yield IngestedTokens(file=current_file, data=text, error=None)

        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")

    async def extract_and_process_image(self, collected_bytes: CollectedBytes) -> str:
        text = await self.extract_text_from_image(collected_bytes)
        return await self.process_data(text)

    async def extract_text_from_image(self, collected_bytes: CollectedBytes) -> str:
        image = Image.open(io.BytesIO(collected_bytes.data))
        text = pytesseract.image_to_string(image)
        return text

    async def process_data(self, text: str) -> str:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
