import json
from typing import AsyncGenerator

import aiofiles
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import GcsCollectConfig
from querent.config.collector.collector_config import CollectorBackend
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.uri import Uri
from querent.common import common_errors
from google.cloud import storage
from dotenv import load_dotenv

from querent.logging.logger import setup_logger

load_dotenv()


class GCSCollector(Collector):
    def __init__(self, config: GcsCollectConfig):
        self.bucket_name = config.bucket
        self.credentials = json.loads(config.credentials)
        self.client = None
        self.chunk_size = 1024
        if config.chunk and config.chunk.isdigit():
            self.chunk_size = int(config.chunk)
        self.logger = setup_logger(__name__, "GCSCollector")

    async def connect(self):
        if not self.client:
            try:
                self.client = storage.Client.from_service_account_info(self.credentials)
            except ConnectionError as exc:
                self.logger.error(f"Error connecting to GCS: {exc}")
                raise common_errors.ConnectionError(
                    "Please pass the credentials"
                ) from exc

    async def disconnect(self):
        try:
            if self.client is not None:
                self.client.close()
                self.client = None
        except Exception as exc:
            self.logger.error(f"Error disconnecting from GCS: {exc}")

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        # Make sure to connect the client before using it
        if not self.client:
            await self.connect()

        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blobs = list(bucket.list_blobs())  # Convert to a list
            for blob in blobs:
                async for chunk in self.stream_blob(blob):
                    yield CollectedBytes(file=blob.name, data=chunk, error=None)
                yield CollectedBytes(file=blob.name, data=None, error=None, eof=True)
        except Exception as e:
            # Handle exceptions gracefully, e.g., log the error
            self.logger.error(f"Error connecting to GCS: {e}")
        finally:
            # Disconnect the client when done
            await self.disconnect()

    async def stream_blob(self, blob):
        try:
            with blob.open("rb") as blob_file:
                while True:
                    chunk = blob_file.read(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk
        except PermissionError as exc:
            raise common_errors.PermissionError(
                f"Unable to open this file {blob_file}, getting error as {exc}"
            ) from exc
        except OSError as exc:
            raise common_errors.OSError(
                f"Getting OS Error on file {blob_file}, as {exc}"
            ) from exc
        except Exception as exc:
            raise common_errors.UnknownError(
                f"Getting OS Error on file {blob_file}, as {exc}"
            ) from exc


class GCSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Gcs

    def resolve(self, uri: Uri, config: GcsCollectConfig) -> Collector:
        return GCSCollector(config)
