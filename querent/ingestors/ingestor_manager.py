"""
Ingestor manager, for managing all the factories with backend
"""
from typing import AsyncGenerator, List, Optional
from querent.collectors.collector_base import Collector
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
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
from querent.ingestors.github.github_ingestor import GithubIngestorFactory
from querent.ingestors.code.code_ingestor import CodeIngestorFactory
from functools import lru_cache

from querent.logging.logger import setup_logger


class IngestorFactoryManager:
    """Factory manager"""

    PROGRAMMING_LANGUAGES = [
        "py",
        "pyw",
        "pyp",
        "js",
        "mjs",
        "java",
        "cpp",
        "h",
        "hpp",
        "c",
        "h",
        "cs",
        "rb",
        "swift",
        "php",
        "php3",
        "php4",
        "php5",
        "css",
        "go",
        "rs",
        "kt",
        "ts",
        "pl",
        "sql",
        "r",
        "m",
        "sh",
        "bash",
        "zsh",
        "dart",
        "scala",
        "groovy",
        "lua",
        "m",
        "vb",
    ]

    def __init__(self):
        self.collectors = []
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
            IngestorBackend.GITHUB.value: GithubIngestorFactory(),
            # Add more mappings as needed
        }
        # this collects each file and its CollectBytes
        self.file_caches = dict()
        self.logger = setup_logger(__name__, "IngestorFactoryManager")

    async def set_collectors(self, collectors: List[Collector]):
        self.collectors = collectors

    async def get_factory(self, file_extension: str) -> IngestorFactory:
        """get_factory to match factory based on file extension"""
        if file_extension is None or file_extension == "":
            return TextIngestorFactory()
        if file_extension in self.PROGRAMMING_LANGUAGES:
            return CodeIngestorFactory()
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

    async def ingest_file_async(self, collected_bytes_list: List[CollectedBytes]):
        try:
            file_extension = collected_bytes_list[0].file_extension
            ingestor = await self.get_ingestor(file_extension)
            if ingestor is not None:
                async for tokens in ingestor.ingest(collected_bytes_list):
                    yield tokens
            else:
                self.logger.warning(
                    f"Unsupported file extension {file_extension} for file {collected_bytes_list[0].file}"
                )
        except Exception as e:
            self.logger.error(
                f"Error ingesting file {collected_bytes_list[0].file}: {str(e)}"
            )

    async def ingest_all_async(self) -> AsyncGenerator[IngestedTokens, None]:
        """ingest to ingest data"""
        for collector in self.collectors:
            async for collected_bytes in collector.poll():
                file_extension = collected_bytes.file_extension
                if not await self.supports(file_extension):
                    self.logger.warning(
                        f"Unsupported file extension {file_extension} for file {collected_bytes.file}"
                    )
                    continue

                current_file = collected_bytes.file

                if current_file not in self.file_caches:
                    # Start a new cache for this file
                    self.file_caches[current_file] = [collected_bytes]
                else:
                    # Add bytes to the existing cache
                    self.file_caches[current_file].append(collected_bytes)

                # Check if this is the end of the file
                if collected_bytes.eof:
                    collected_bytes_list = self.file_caches.pop(current_file)
                    await self.ingest_file_async(collected_bytes_list)
