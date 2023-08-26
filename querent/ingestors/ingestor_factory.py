

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

class Ingestor(str, Enum):
    PDF = "pdf"
    TEXT = "txt" | "text"
    DOCX = "docx" | "doc"
    CSV = "csv" | "comma-separated-values" | "comma-separated"
    XLSX = "xlsx" | "xls" | "excel"
    JSON = "json"
    XML = "xml"
    HTML = "html"
    YAML = "yaml" | "yml"
    MARKDOWN = "markdown" | "md"
    IMG = "image" | "img"
    PNG = "png"
    JPG = "jpg" | "jpeg"
    GIF = "gif"
    WEBRTC = "webrtc"
    MP3 = "mp3"
    MP4 = "mp4"
    MOV = "mov"
    AVI = "avi"
    WAV = "wav"
    Unsupported = "unsupported"

class IngestorFactory(ABC):
    @abstractmethod
    async def supports(self, file_extension: str) -> bool:
        pass

    @abstractmethod
    async def create(self, file_extension: str) -> Optional[Ingestor]:
        pass



class IngestorFactoryManager:
    def __init__(self):
        self.ingestor_factories = {
            #Ingestor.PDF.value: PdfIngestor(),
            #Ingestor.TEXT.value: TextIngestor(),
            # Add more mappings as needed
        }

    async def get_factory(self, file_extension: str) -> IngestorFactory:
        return self.ingestor_factories.get(file_extension.lower(), UnsupportedIngestor("Unsupported file extension"))

    async def get_ingestor(self, file_extension: str) -> Optional[Ingestor]:
        factory = self.get_factory(file_extension)
        return factory.create(file_extension)
    
    async def supports(self, file_extension: str) -> bool:
        factory = self.get_factory(file_extension)
        return factory.supports(file_extension)
    
class UnsupportedIngestor(IngestorFactory):
    def __init__(self, message: str):
        self.message = message

    async def supports(self, file_extension: str) -> bool:
        return False

    async def create(self, file_extension: str) -> Optional[Ingestor]:
        return None
