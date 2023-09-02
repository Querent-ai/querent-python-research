import asyncio
from typing import AsyncGenerator

import aiofiles
from querent.config.collector_config import CollectorBackend, S3CollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri
import boto3
import os
from dotenv import load_dotenv

load_dotenv()

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
aws_bucket_name = os.getenv('AWS_BUCKET_NAME')


class AWSCollector(Collector):
    def __init__(self, config: S3CollectConfig, prefix: str):
        self.bucket_name = config.bucket
        self.region = config.region
        self.access_key = config.access_key
        self.secret_key = config.secret_key
        self.chunk_size = config.chunk
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
        self.prefix = prefix

    async def connect(self):
        pass  # No asynchronous connection needed for boto3

    async def disconnect(self):
        pass  # No asynchronous disconnect needed for boto3

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=self.prefix)

        for obj in response.get('Contents', []):
            file = self.download_object(obj['Key'])
            async for chunk in self.read_chunks(file):
                yield CollectorResult({"object_key": obj['Key'], "chunk": chunk})

    async def read_chunks(self, file):
        while True:
            chunk = file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def download_object(self, object_key):
        file_path = object_key  # Set your desired file path
        self.s3_client.download_file(
            self.bucket_name, object_key, file_path)
        return open(file_path, 'rb')


class AWSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.S3

    def resolve(self, uri: Uri, config: S3CollectConfig) -> Collector:
        config = S3CollectConfig(bucket=aws_bucket_name, region=aws_region,
                                 access_key=aws_access_key_id, secret_key=aws_secret_access_key)
        return AWSCollector(config, "")
