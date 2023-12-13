from typing import AsyncGenerator, List
import json
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.ingestors.base_ingestor import BaseIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.common import common_errors
from querent.common.types.ingested_tokens import IngestedTokens
from querent.logging.logger import setup_logger


class JsonIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"json", "jira"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return JsonIngestor(processors)


class JsonIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.JSON)
        self.processors = processors
        self.logger = setup_logger(__name__, "JsonIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        try:
            current_file = None
            collected_bytes = b""
            try:
                async for chunk_bytes in poll_function:
                    if chunk_bytes.is_error() or chunk_bytes.is_eof():
                        continue

                    if chunk_bytes.file != current_file:
                        if current_file:
                            async for json_objects in self.extract_and_process_json(
                                CollectedBytes(file=current_file, data=collected_bytes)
                            ):
                                yield IngestedTokens(
                                    file=current_file, data=[json_objects], error=None
                                )
                        if current_file:
                            yield IngestedTokens(
                                file=current_file,
                                data=None,
                                error=None,
                            )
                        collected_bytes = b""
                        current_file = chunk_bytes.file

                    collected_bytes += chunk_bytes.data

            except json.JSONDecodeError:
                yield IngestedTokens(
                    file=current_file, data=None, error="JSON Decode Error"
                )
            finally:
                async for json_objects in self.extract_and_process_json(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield IngestedTokens(
                        file=current_file, data=[json_objects], error=None
                    )
                yield IngestedTokens(file=current_file, data=None, error=None)

        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")

    async def extract_and_process_json(self, collected_bytes: CollectedBytes) -> str:
        try:
            json_data = collected_bytes.data.decode("utf-8")
            processed_text = await self.process_data(json_data)
            yield processed_text
        except json.JSONDecodeError as exc:
            raise common_errors.JsonDecodeError(
                f"Getting UnicodeDecodeError on this file {collected_bytes.file}"
            ) from exc

        except UnicodeDecodeError as exc:
            raise common_errors.UnicodeDecodeError(
                f"Getting UnicodeDecodeError on this file {collected_bytes.file}"
            ) from exc
        except LookupError as exc:
            raise common_errors.LookupError(
                f"Getting LookupError on this file {collected_bytes.file}"
            ) from exc
        except TypeError as exc:
            raise common_errors.TypeError(
                f"Getting TypeError on this file {collected_bytes.file}"
            ) from exc

    async def process_data(self, text: str) -> str:
        if self.processors is None or len(self.processors) == 0:
            return text
        try:
            processed_data = text
            for processor in self.processors:
                processed_data = await processor.process_text(processed_data)
            return processed_data
        except Exception as e:
            self.logger.error(f"Error while processing text: {e}")
