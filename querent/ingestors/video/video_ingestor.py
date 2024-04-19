import io
from typing import List, AsyncGenerator
import moviepy.editor as mp
from querent.ingestors.audio.audio_ingestors import AudioIngestor
from querent.ingestors.ingestor_factory import IngestorFactory
from querent.processors.async_processor import AsyncProcessor
from querent.ingestors.base_ingestor import BaseIngestor
from querent.config.ingestor.ingestor_config import IngestorBackend
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.types.ingested_tokens import IngestedTokens
from querent.logging.logger import setup_logger
import ffmpeg

class VideoIngestorFactory(IngestorFactory):
    SUPPORTED_EXTENSIONS = {"mp4"}

    async def supports(self, file_extension: str) -> bool:
        return file_extension.lower() in self.SUPPORTED_EXTENSIONS

    async def create(
        self, file_extension: str, processors: List[AsyncProcessor]
    ) -> BaseIngestor:
        if not await self.supports(file_extension):
            return None
        return VideoIngestor(processors)


class VideoIngestor(BaseIngestor):
    def __init__(self, processors: List[AsyncProcessor]):
        super().__init__(IngestorBackend.MP4)
        self.audio_processor = AudioIngestor(processors)
        self.processors = processors
        self.logger = setup_logger(__name__, "VideoIngestor")

    async def ingest(self, poll_function: AsyncGenerator[CollectedBytes, None]) -> AsyncGenerator[IngestedTokens, None]:
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
                    # We have a new file, process the old one
                    async for text in self.extract_and_process_video(
                        CollectedBytes(file=current_file, data=collected_bytes)
                    ):
                        yield IngestedTokens(file=current_file, data=[text], error=None, doc_source=chunk_bytes.doc_source)
                    # Ensure a final yield for the last processed text
                    yield IngestedTokens(
                        file=current_file,
                        data=None,
                        error=None,
                        doc_source=chunk_bytes.doc_source
                    )
                    collected_bytes = b""
                    current_file = chunk_bytes.file
                collected_bytes += chunk_bytes.data
        except Exception as e:
            yield IngestedTokens(file=current_file, data=None, error=f"Exception: {e}", doc_source=chunk_bytes.doc_source)
        finally:
            if collected_bytes:  # Check if there's data left to process for the last file
                async for text in self.extract_and_process_video(
                    CollectedBytes(file=current_file, data=collected_bytes)
                ):
                    yield IngestedTokens(file=current_file, data=[text], error=None, doc_source=chunk_bytes.doc_source)
                # Ensure a final yield for the last processed text
                yield IngestedTokens(file=current_file, data=None, error=None, doc_source=chunk_bytes.doc_source)

    async def extract_and_process_video(self, collected_bytes: CollectedBytes) -> AsyncGenerator[str, None]:
        text = ""
        async for video_text in self.extract_text_from_video(collected_bytes):
            text += video_text
        processed_text = await self.process_data(text)
        yield processed_text


    async def extract_text_from_video(self, collected_bytes: CollectedBytes) -> AsyncGenerator[str, None]:
        input_video_stream = io.BytesIO(collected_bytes.data)
        try:
            process = (
                ffmpeg
                .input('pipe:0', format='mp4')
                .output('pipe:1', format='wav')
                .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True, overwrite_output=True)
            )
            input_video_stream.seek(0)
            process.stdin.write(input_video_stream.read())
            process.stdin.close()
            output_audio_data = process.stdout.read()
            await process.wait()
            async for text in self.audio_processor.extract_and_process_audio(
                CollectedBytes(file=collected_bytes.file, data=output_audio_data)
            ):
                yield text

        except Exception as e:
            self.logger.error(f"Failed to extract text from video: {e}")

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
