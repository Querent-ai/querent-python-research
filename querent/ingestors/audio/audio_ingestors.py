from typing import List, AsyncGenerator
import io
import speech_recognition as sr
from pydub import AudioSegment

from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens


class AudioIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"mp3"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return AudioIngestor(processors)


class AudioIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.MP3)
        self.processors = processors

    async def ingest(
        self, poll_function: AsyncGenerator[CollectedBytes, None]
    ) -> AsyncGenerator[IngestedTokens, None]:
        current_file = None
        collected_bytes = b""
        try:
            async for chunk_bytes in poll_function:
                if chunk_bytes.is_error():
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

    async def extract_and_process_audio(
        self, collected_bytes: CollectedBytes
    ) -> AsyncGenerator[IngestedTokens, None]:
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
        try:
            recognized_text = recognizer.recognize_google(audio_data, language="en-US")
            processed_text = await self.process_data(recognized_text)
            yield IngestedTokens(
                file=collected_bytes.file, data=[processed_text], error=None
            )
        except sr.UnknownValueError:
            print("Could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(e)

    async def process_data(self, text: str) -> str:
        processed_data = text
        for processor in self.processors:
            processed_data = await processor.process_text(processed_data)
        return processed_data
