import io
from typing import AsyncGenerator
from botocore.exceptions import (
    NoCredentialsError,
)
from querent.common.types.collected_bytes import (
    CollectedBytes,
)  # Import for handling authentication errors
from querent.config.collector.collector_config import CollectorBackend, S3CollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.uri import Uri
import boto3

from querent.logging.logger import setup_logger


class AWSCollector(Collector):
    def __init__(self, config: S3CollectConfig, prefix: str):
        self.bucket_name = config.bucket
        self.region = config.region
        self.access_key = config.access_key
        self.secret_key = config.secret_key
        self.chunk_size = 1024  # Default value
        if config.chunk and config.chunk.isdigit():
            self.chunk_size = int(config.chunk)
        self.logger = setup_logger(__name__, "AWSCollector")

    async def connect(self):
        # Initialize the S3 client with proper error handling for credentials
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )
        except NoCredentialsError:
            raise Exception("AWS credentials are not set properly.")

    async def disconnect(self):
        # No asynchronous disconnect needed for boto3
        pass

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        if not self.s3_client:
            await self.connect()

        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)

            for obj in response.get("Contents", []):
                file = self.download_object_as_byte_stream(obj["Key"])
                async for chunk in self.read_chunks(file):
                    yield CollectedBytes(file=obj["Key"], data=chunk, error=None)
                yield CollectedBytes(file=obj["Key"], data=None, error=None, eof=True)

        except PermissionError as exc:
            self.logger.error(f"Getting Permission Error on file {file}, as {exc}")
        except OSError as exc:
            self.logger.error(f"Getting OS Error on file {file}, as {exc}")
        finally:
            await self.disconnect()  # Disconnect when done

    async def read_chunks(self, file):
        while True:
            chunk = file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def download_object_as_byte_stream(self, object_key):
        byte_stream = io.BytesIO()
        self.s3_client.download_fileobj(self.bucket_name, object_key, byte_stream)
        byte_stream.seek(0)  # Rewind the stream to the beginning
        return byte_stream


class AWSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.S3

    def resolve(self, uri: Uri, config: S3CollectConfig) -> Collector:
        return AWSCollector(config, uri)
