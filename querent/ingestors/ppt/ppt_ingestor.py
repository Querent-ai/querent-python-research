"""Ingestor class for ppt files"""
from typing import List, AsyncGenerator
from io import BytesIO
from pptx import Presentation
from pptx.exc import InvalidXmlError
from tika import parser
from zipfile import BadZipFile

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common import common_errors


class PptIngestorFactory(IngestorFactory):
    """Ingestor factory for ppts"""

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
    """Ingestor for ppt files"""

    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.PDF)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[str, None]:
        """ "Function for ingesting the ppt stream"""
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
                    async for page_text in self.extract_and_process_ppt(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield page_text
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            # TODO handle exception
            yield None
        finally:
            # process the last file
            async for page_text in self.extract_and_process_ppt(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield page_text
            pass

    async def extract_and_process_ppt(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[str, None]:
        try:
            text = await self.extract_text_from_ppt(collected_bytes)
            processed_text = await self.process_data(text)
            yield processed_text
        except Exception as exc:
            yield None

    async def extract_text_from_ppt(self, collected_bytes: CollectedBytes) -> str:
        try:
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

            else:
                raise common_errors.WrongPptFileError(
                    f"Given file is not ppt {collected_bytes.file}"
                )
        except InvalidXmlError as exc:
            raise common_errors.InvalidXmlError(
                f"The following file is not in proper xml format {collected_bytes.file}"
            ) from exc
        except BadZipFile as exc:
            raise common_errors.BadZipFile(
                f"The following file is not a zip file{collected_bytes.file}"
            ) from exc

    async def process_data(self, text: str) -> List[str]:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process(processed_data)
        return processed_data
