import asyncio
from typing import AsyncGenerator

import aiofiles
from querent.config.collector_config import GcsCollectConfig
from querent.config.collector_config import CollectorBackend
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri
import aiohttp
from google.cloud import storage


class GCSCollector(Collector):
    def __init__(self, config: GcsCollectConfig):
        self.bucket_name = config.bucket
        self.credentials = config.credentials_path
        self.chunk_size = config.chunk

    async def connect(self):
        self.client = storage.Client.from_service_account_json(
            self.credentials)
        self.bucket = self.client.get_bucket(self.bucket_name)

    async def disconnect(self):
        if self.client is not None:
            self.client.close()

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        blobs = self.bucket.list_blobs()
        for blob in blobs:
            async with self.download_blob(blob) as file:
                async for chunk in self.read_chunks(file):
                    yield CollectorResult({"object_key": blob.name, "chunk": chunk})

    async def read_chunks(self, file):
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def download_blob(self, blob):
        file = aiofiles.open(blob.name, 'wb')
        # Manually enter the context manager since aiofiles doesn't natively support async context management
        await file.__aenter__()
        with blob.open("rb") as blob_file:
            await file.write(await blob_file.read())
        return file


class GCSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Gcs

    def resolve(self, uri: Uri, config: GcsCollectConfig) -> Collector:
        config = GcsCollectConfig(
            bucket='your_bucket_name', credentials_path='path_to_your_credentials.json')
        return GCSCollector(config)
