import asyncio
from asyncio import Queue
from typing import AsyncGenerator, List, Optional
from cachetools import LRUCache, cachedmethod
from querent.channel.channel_interface import ChannelCommandInterface

from querent.collectors.collector_base import Collector
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.email.email_ingestor import EmailIngestorFactory
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
import asyncio

from querent.logging.logger import setup_logger
from querent.processors.async_processor import AsyncProcessor


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

    def __init__(
        self,
        collectors: Optional[List[Collector]] = None,
        processors: Optional[List[AsyncProcessor]] = None,
        cache_size: Optional[int] = 100,
        result_queue: Optional[Queue] = None,
        tokens_feader: Optional[ChannelCommandInterface] = None,
    ):
        self.collectors = collectors
        self.processors = processors
        if self.processors is None:
            self.processors = []
        if self.collectors is None:
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
            IngestorBackend.Slack.value: TextIngestorFactory(is_token_stream=True),
            IngestorBackend.Email.value: EmailIngestorFactory(),
            IngestorBackend.Jira.value: JsonIngestorFactory(),
            # Add more mappings as needed
        }
        self.file_caches = LRUCache(maxsize=cache_size)
        self.result_queue = result_queue
        self.tokens_feader = tokens_feader
        self.logger = setup_logger(__name__, "IngestorFactoryManager")

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
        factory = await self.get_factory(file_extension)
        return await factory.create(file_extension, self.processors)

    async def supports(self, file_extension: str) -> bool:
        """check if extension supports factory"""
        factory = await self.get_factory(file_extension)
        return factory.supports(file_extension)

    @cachedmethod(cache=lambda self: self.file_caches)
    async def ingest_file_async(
        self,
        file_id: str,
        result_queue: Optional[Queue] = None,
        tokens_feader: Optional[ChannelCommandInterface] = None,
    ):
        try:
            collected_bytes_list = self.file_caches.pop(file_id)
            file_extension = collected_bytes_list[0].extension
            ingestor = await self.get_ingestor(file_extension)
            if ingestor is not None:

                async def chunk_generator() -> AsyncGenerator[CollectedBytes, None]:
                    for chunk in collected_bytes_list:
                        if chunk.eof or chunk.error is not None:
                            break
                        yield chunk

                async for chunk_tokens in ingestor.ingest(chunk_generator()):
                    if result_queue is not None:
                        result_queue.put_nowait(chunk_tokens)
                    if tokens_feader is not None:
                        tokens_feader.send_tokens_in_rust({
                            "data": chunk_tokens.data if type(chunk_tokens) == IngestedTokens else chunk_tokens.ocr_text,
                            "file": chunk_tokens.file,
                            "is_token_stream": True,
                        })
            else:
                self.logger.warning(
                    f"Unsupported file extension {file_extension} for file {collected_bytes_list[0].file}"
                )
        except Exception as e:
            self.logger.error(
                f"Error ingesting file {collected_bytes_list[0].file}: {str(e)}"
            )

    async def ingest_collector_async(
        self,
        collector: Collector,
        result_queue: Optional[Queue] = None,
        token_feader: Optional[ChannelCommandInterface] = None,
    ):
        """Asynchronously ingest data from a single collector."""
        async for collected_bytes in collector.poll():
            current_file = collected_bytes.file

            if current_file not in self.file_caches:
                if not collected_bytes.eof:
                    self.file_caches[current_file] = [collected_bytes]
            else:
                if not collected_bytes.eof:
                    self.file_caches[current_file].append(collected_bytes)

            # Check if this is the end of the file
            if collected_bytes.eof:
                # Try to ingest the ongoing file even if the cache is full
                try:
                    await self.ingest_file_async(
                        current_file, result_queue, token_feader
                    )
                except Exception as e:
                    self.logger.error(f"Error ingesting file {current_file}: {str(e)}")

                # Wait for ongoing file processing to complete before checking for the next file
                while current_file in self.file_caches:
                    await asyncio.sleep(0.1)

    async def ingest_all_async(self):
        """Asynchronously ingest data from all collectors concurrently."""
        ingestion_tasks = [
            self.ingest_collector_async(
                collector, self.result_queue, self.tokens_feader
            )
            for collector in self.collectors
        ]
        await asyncio.gather(*ingestion_tasks)
        if self.result_queue is not None:
            await self.result_queue.put(None)
