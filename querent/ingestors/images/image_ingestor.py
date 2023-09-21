from typing import List, AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor_config import IngestorBackend
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.ingestor_errors import (
    FileNotFoundError,
    IOError,
    UnidentifiedImageError,
)
import pytesseract
from PIL import Image, UnidentifiedImageError
import io


class ImageIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"jpg", "jpeg", "png"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return ImageIngestor(processors)


class ImageIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.JPG)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[List[str], None]:
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
                        yield text
                    collected_bytes = b""
                    current_file = chunk_bytes.file

                collected_bytes += chunk_bytes.data

            if current_file:
                text = await self.extract_and_process_image(
                    CollectedBytes(file=current_file, data=collected_bytes)
                )
                yield text

        except Exception as e:
            print(e)
            yield []

    async def extract_and_process_image(self, collected_bytes: CollectedBytes) -> str:
        text = await self.extract_text_from_image(collected_bytes)
        return await self.process_data(text)

    async def extract_text_from_image(self, collected_bytes: CollectedBytes) -> str:
        try:
            image = Image.open(io.BytesIO(collected_bytes.data))

        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Given file with name as {collected_bytes.file} not found"
            ) from exc
        except IOError as exc:
            raise IOError(
                f"Unable to open given file with name as {collected_bytes.file}"
            ) from exc
        except UnidentifiedImageError as exc:
            raise UnidentifiedImageError(
                f"Unable to open the given file with given name {collected_bytes.file}"
            ) from exc

        text = pytesseract.image_to_string(image)

        return text

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
