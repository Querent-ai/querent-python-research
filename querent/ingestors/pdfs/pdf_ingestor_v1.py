from typing import AsyncGenerator, List
import fitz
from querent.common.types.collected_bytes import CollectedBytes  # PyMuPDF
from querent.ingestors.ingestor_factory import Ingestor, IngestorFactory


class PdfIngestor(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"pdf"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(self, file_extension: str) -> Ingestor:
        if not self.supports(file_extension):
            return None
        return PdfIngestor()


class PdfIngestor(Ingestor):
    def __init__(self):
        super().__init__(Ingestor.PDF)

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[List[str], None]:
        try:
            async for collected_bytes in poll_function():
                text = self.extract_text_from_pdf(collected_bytes)
                # Add more processing logic here if needed
                sentences = self.split_into_sentences(text)
                yield sentences
        except Exception as e:
            yield []

    def extract_text_from_pdf(self, collected_bytes):
        pdf_data = collected_bytes.unwrap()
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        text = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            text += page.get_text()
        pdf_document.close()
        return text

    def split_into_sentences(self, text):
        # Implement logic to split text into sentences
        # You can use NLTK, spaCy, or custom regex-based logic
        # Return a list of sentences
        return []
