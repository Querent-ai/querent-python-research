import base64
from typing import List, AsyncGenerator
import io
import uuid
import pandas as pd
import openpyxl
from PIL import Image
import pytesseract

from querent.common.types.ingested_images import IngestedImages
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.ingestors.base_ingestor import BaseIngestor
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import (
    IngestedTokens,
)  # Added import for the return type
from querent.logging.logger import setup_logger


class XlsxIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"xlsx"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return XlsxIngestor(processors)


class XlsxIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.XLSX)
        self.processors = processors
        self.logger = setup_logger(__name__, "XlsxIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for data in self.extract_and_process_xlsx(
                        CollectedBytes(file=current_file, data=collected_bytes), chunk_bytes.doc_source
                    ):
                        yield data
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                        doc_source=chunk_bytes.doc_source
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}", doc_source=chunk_bytes.doc_source)
        finally:
            async for data in self.extract_and_process_xlsx(
                CollectedBytes(file=current_file, data=collected_bytes), chunk_bytes.doc_source
            ):
                yield data
            yield IngestedTokens(file=current_file, data=None, error=None, doc_source=chunk_bytes.doc_source)

    async def extract_and_process_xlsx(
        self, collected_bytes: CollectedBytes, doc_source
    ) -> AsyncGenerator[pd.DataFrame, None]:
        async for data in self.extract_text_from_xlsx(collected_bytes, doc_source):
            yield data

    async def extract_text_from_xlsx(
        self, collected_bytes: CollectedBytes, doc_source):
        try:
            excel_buffer = io.BytesIO(collected_bytes.data)
            workbook = openpyxl.load_workbook(excel_buffer, data_only=True)

            for sheet in workbook:
                df = pd.read_excel(excel_buffer, sheet_name=sheet.title)
                df['Sheet'] = sheet.title
                df = df.to_string()
                processed_data = await self.process_data(df)

        
                print(f"Processing sheet: {sheet.title}")
                for image in sheet._images:
                    img = image._data()
                    ocr_text = await self.get_ocr_from_image(image=img)
                    if not ocr_text:
                        continue
                    
                    yield IngestedImages(
                        file=collected_bytes.file,
                        image=str(base64.b64encode(img)),
                        image_name=f"{str(uuid.uuid4())}.jpg",
                        page_num=sheet.title,
                        text=processed_data,
                        coordinates=None,
                        ocr_text=[ocr_text],
                        doc_source=doc_source,
                    )

                 # Prepare data for DataFrame
                yield IngestedTokens(
                    file=collected_bytes.file,
                    data=processed_data,
                    error=None,
                    doc_source=doc_source
                )
                
        except Exception as e:
            self.logger.error("Exception-{e}")

    async def get_ocr_from_image(self, image):
        """Implement this to return ocr text of the image"""
        try:
            image = Image.open(io.BytesIO(image))

            image_status = await self.analyze_image(image)
            if not image_status:
                return
            text = pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.error("Exception-{e}")
            raise e
        return str(text).encode("utf-8").decode("utf-8")

    async def process_data(self, text: str) -> str:
        if self.processors is None or len(self.processors) == 0:
            return [text]
        try:
            processed_data = text
            for processor in self.processors:
                processed_data = await processor.process_text(processed_data)
            return [processed_data]
        except Exception as e:
            self.logger.error(f"Error while processing text: {e}")
