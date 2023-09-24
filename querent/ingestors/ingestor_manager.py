"""
Ingestor manager, for managing all the factories with backend
"""
from typing import Optional
from querent.config.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory, UnsupportedIngestor
from querent.ingestors.pdfs.pdf_ingestor_v1 import PdfIngestorFactory
from querent.ingestors.texts.text_ingestor import TextIngestorFactory
from querent.ingestors.audio.audio_ingestors import AudioIngestorFactory
from querent.ingestors.json.json_ingestor import JsonIngestorFactory
from querent.ingestors.images.image_ingestor import ImageIngestorFactory
from querent.ingestors.doc.doc_ingestor import DocIngestorFactory
from querent.ingestors.csv.csv_ingestor import CsvIngestorFactory
from querent.ingestors.video.video_ingestor import VideoIngestorFactory
from querent.ingestors.xlsx.xlsx_ingestor import XlsxIngestorFactory
from querent.ingestors.ppt.ppt_ingestor import PptIngestorFactory
from querent.ingestors.xml.xml_ingestor import XmlIngestorFactory
from querent.ingestors.html.html_ingestor import HtmlIngestorFactory


class IngestorFactoryManager:
    """Factory manager"""

    def __init__(self):
        self.ingestor_factories = {
            IngestorBackend.PDF.value: PdfIngestorFactory(),
            IngestorBackend.TEXT.value: TextIngestorFactory(),
            IngestorBackend.MP3.value: AudioIngestorFactory(),
            IngestorBackend.WAV.value: AudioIngestorFactory(),
            IngestorBackend.JSON.value: JsonIngestorFactory(),
            IngestorBackend.JPG.value: ImageIngestorFactory(),
            IngestorBackend.PNG.value: ImageIngestorFactory(),
            IngestorBackend.DOCX.value: DocIngestorFactory(),
            IngestorBackend.DOC.value: DocIngestorFactory(),
            IngestorBackend.CSV.value: CsvIngestorFactory(),
            IngestorBackend.XLSX.value: XlsxIngestorFactory(),
            IngestorBackend.PPT.value: PptIngestorFactory(),
            IngestorBackend.PPTX.value: PptIngestorFactory(),
            IngestorBackend.XML.value: XmlIngestorFactory(),
            IngestorBackend.HTML.value: HtmlIngestorFactory(),
            IngestorBackend.MP4.value: VideoIngestorFactory(),
            # Add more mappings as needed
        }

    async def get_factory(self, file_extension: str) -> IngestorFactory:
        """get_factory to match factory based on file extension"""
        return self.ingestor_factories.get(
            file_extension.lower(), UnsupportedIngestor("Unsupported file extension")
        )

    async def get_ingestor(self, file_extension: str) -> Optional[BaseIngestor]:
        """get_ingestor to get factory for that extension"""
        factory = self.get_factory(file_extension)
        return factory.create(file_extension)

    async def supports(self, file_extension: str) -> bool:
        """check if extension supports factory"""
        factory = self.get_factory(file_extension)
        return factory.supports(file_extension)
