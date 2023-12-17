from typing import List, AsyncGenerator
from querent.common.types.collected_bytes import CollectedBytes
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens


class CodeIngestorFactory(IngestorFactory):
    PROGRAMMING_LANGUAGES = {
        "Python": ["py", "pyw", "pyp"],
        "JavaScript": ["js", "mjs"],
        "Java": ["java"],
        "C++": ["cpp", "h", "hpp"],
        "C": ["c", "h"],
        "C#": ["cs"],
        "Ruby": ["rb"],
        "Swift": ["swift"],
        "PHP": ["php", "php3", "php4", "php5", "phtml"],
        "HTML": ["html", "htm"],
        "CSS": ["css"],
        "Go": ["go"],
        "Rust": ["rs"],
        "Kotlin": ["kt"],
        "TypeScript": ["ts"],
        "Perl": ["pl"],
        "SQL": ["sql"],
        "R": ["r"],
        "MATLAB": ["m"],
        "Shell Scripting": ["sh", "bash", "zsh"],
        "Dart": ["dart"],
        "Scala": ["scala"],
        "Groovy": ["groovy"],
        "Lua": ["lua"],
        "Objective-C": ["m"],
        "VB.NET": ["vb"],
    }

    async def supports(self, file_extension: str) -> bool:
        for language, extensions in self.PROGRAMMING_LANGUAGES.items():
            if file_extension in extensions:
                return True
        return False

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return CodeIngestor(processors)


class CodeIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.TEXT)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        collected_bytes = b""
        current_file = None
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    continue

                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    async for line in self.extract_code_from_bytes(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(
                            file=current_file,
                            data=[line],
                            error=None,
                        )
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
            if current_file:
                async for line in self.extract_code_from_bytes(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield IngestedTokens(
                        file=current_file,
                        data=[line],
                        error=None,
                    )
                yield IngestedTokens(file=current_file, data=None, error=None)
        except Exception as exc:
            yield IngestedTokens(
                file=current_file, data=None, error=f"Exception: {exc}"
            )
            raise Exception from exc

    async def extract_code_from_bytes(
        self, chunk_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedTokens, None]:
        try:
            code_bytes = chunk_bytes.data.decode("UTF-8")
            yield code_bytes
        except UnicodeDecodeError as exc:
            raise common_errors.UnicodeDecodeError(
                f"Getting UnicodeDecodeError on this file {chunk_bytes.file}"
            ) from exc
        except LookupError as exc:
            raise common_errors.LookupError(
                f"Getting LookupError on this file {chunk_bytes.file}"
            ) from exc
        except TypeError as exc:
            raise common_errors.TypeError(
                f"Getting TypeError on this file {chunk_bytes.file}"
            ) from exc
