from typing import List, AsyncGenerator
import io
import speech_recognition as sr
from pydub import AudioSegment

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.common_errors import (
    UnknownValueError,
    RequestError,
    IndexErrorException,
    UnknownError,
)
from querent.common.types.ingested_tokens import IngestedTokens
from querent.logging.logger import setup_logger


class AudioIngestorFactory(IngestorFactory):
    """
    Factory class for creating AudioIngestor instances.

    This class defines methods to check if a given file extension is supported
    and to create an AudioIngestor object if the extension is supported.
    """

    SUPPORTED_EXTENSIONS = {"mp3"}

    async def supports(self, file_extension: str) -> bool:
        """
        Check if the specified file extension is supported for audio ingestion.

        Args:
            file_extension (str): The file extension to check.

        Returns:
            bool: True if the extension is supported, False otherwise.
        """
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        """
        Create an AudioIngestor instance if the specified extension is supported.

        Args:
            file_extension (str): The file extension to create an ingestor for.
            processors (List[AsyncProcessor]): List of processors to apply to the ingested data.

        Returns:
            BaseIngestor: An AudioIngestor instance or None if the extension is not supported.
        """
        if not await self.supports(file_extension):
            return None
        return AudioIngestor(processors)


class AudioIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.MP3)
        self.processors = processors
        self.logger = setup_logger(__name__, "AudioIngestor")

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error() or chunk_bytes.is_eof():
                    # TODO handle error
                    continue
                if current_file is None:
                    current_file = chunk_bytes.file
                elif current_file != chunk_bytes.file:
                    # we have a new file, process the old one
                    async for text in self.extract_and_process_audio(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(file=current_file, data=[text], error=None)
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}")
        finally:
            # process the last file
            async for text in self.extract_and_process_audio(
                CollectedBytes(file=current_file, data=collected_bytes)
            ):
                yield IngestedTokens(file=current_file, data=[text], error=None)

            yield IngestedTokens(file=current_file, data=None, error=None)

    async def extract_and_process_audio(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedTokens, None]:
        # Recognize the text using the recognizer
        try:
            audio_segment = AudioSegment.from_file(
                io.BytesIO(collected_bytes.data), format=collected_bytes.extension
            )
            temp_wave = io.BytesIO()
            audio_segment.export(temp_wave, format="wav")
            # Initialize the recognizer
            recognizer = sr.Recognizer()

            temp_wave.seek(0)
            with sr.AudioFile(temp_wave) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = recognizer.record(source)

            # Recognize the text using the recognizer

            recognized_text = recognizer.recognize_google(audio_data, language="en-US")
            processed_text = await self.process_data(recognized_text)
            yield processed_text
        except sr.UnknownValueError as exc:
            raise UnknownValueError(
                f"The following file gave Unknown Value Error {collected_bytes.file}"
            ) from exc
        except sr.RequestError as exc:
            raise RequestError(
                f"The following file gave Request Error {collected_bytes.file}"
            ) from exc
        except IndexError as exc:
            raise IndexErrorException(
                f"The following file gave Request Error {collected_bytes.file}"
            ) from exc
        except Exception as exc:
            raise UnknownError(
                f"Received unknown error {exc} from the file {collected_bytes.file}"
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
