from typing import Optional
from querent.config.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory, UnsupportedIngestor
from querent.ingestors.pdfs.pdf_ingestor_v1 import PdfIngestorFactory
from querent.ingestors.audio.audio_ingestors import AudioIngestorFactory
from querent.ingestors.json.json_ingestor import JsonIngestorFactory
from querent.ingestors.images.image_ingestor import ImageIngestorFactory


class IngestorFactoryManager:
    def __init__(self):
        self.ingestor_factories = {
            IngestorBackend.PDF.value: PdfIngestorFactory(),
            IngestorBackend.MP3.value: AudioIngestorFactory(),
            IngestorBackend.WAV.value: AudioIngestorFactory(),
            IngestorBackend.JSON.value: JsonIngestorFactory(),
            IngestorBackend.JPG.value: ImageIngestorFactory(),
            IngestorBackend.PNG.value: ImageIngestorFactory(),
            # Ingestor.TEXT.value: TextIngestor(),
            # Add more mappings as needed
        }

    async def get_factory(self, file_extension: str) -> IngestorFactory:
        return self.ingestor_factories.get(
            file_extension.lower(), UnsupportedIngestor("Unsupported file extension")
        )

    async def get_ingestor(self, file_extension: str) -> Optional[BaseIngestor]:
        factory = self.get_factory(file_extension)
        return factory.create(file_extension)

    async def supports(self, file_extension: str) -> bool:
        factory = self.get_factory(file_extension)
        return factory.supports(file_extension)
