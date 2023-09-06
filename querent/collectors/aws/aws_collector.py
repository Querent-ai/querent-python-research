import asyncio
from typing import AsyncGenerator
import io

import aiofiles
from querent.config.collector_config import CollectorBackend, S3CollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri
import boto3


class AWSCollector(Collector):
    def __init__(self, config: S3CollectConfig, prefix: str):
        self.bucket_name = config["bucket"]
        self.region = config["region"]
        self.access_key = config["access_key"]
        self.secret_key = config["secret_key"]
        self.chunk_size = 1024
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        self.prefix = str(prefix)

    async def connect(self):
        pass  # No asynchronous connection needed for boto3

    async def disconnect(self):
        pass  # No asynchronous disconnect needed for boto3

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name)

        for obj in response.get('Contents', []):
            file = self.download_object_as_byte_stream(obj['Key'])
            async for chunk in self.read_chunks(file):
                yield CollectorResult({"object_key": obj['Key'], "chunk": chunk})

    async def read_chunks(self, file):
        while True:
            chunk = file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    # def download_object(self, object_key):
    #     file_path = object_key  # Set your desired file path
    #     self.s3_client.download_file(
    #         self.bucket_name, object_key, file_path)
    #     return open(file_path, 'rb')

    def download_object_as_byte_stream(self, object_key):
        byte_stream = io.BytesIO()
        self.s3_client.download_fileobj(
            self.bucket_name, object_key, byte_stream)
        byte_stream.seek(0)  # Rewind the stream to the beginning
        return byte_stream


class AWSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.S3

    def resolve(self, uri: Uri, config: S3CollectConfig) -> Collector:
        return AWSCollector(config, uri)
