#

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
import os
from dotenv import load_dotenv

load_dotenv()

credentials_info = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
bucket_name = os.getenv("GOOGLE_BUCKET_NAME")


class GCSCollector(Collector):
    def __init__(self, config: GcsCollectConfig):
        self.bucket_name = config.bucket
        self.credentials = config.credentials
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = storage.Client.from_service_account_json(
                self.credentials)

    async def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        # Make sure to connect the client before using it
        await self.connect()

        try:
            bucket = self.client.get_bucket(self.bucket_name)
            blobs = bucket.list_blobs()
            for blob in blobs:
                async with self.download_blob(blob) as file:
                    async for chunk in self.read_chunks(file):
                        yield CollectorResult({"object_key": blob.name, "chunk": chunk})
        finally:
            # Disconnect the client when done
            await self.disconnect()

    async def read_chunks(self, file):
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def download_blob(self, blob):
        file = aiofiles.open(blob.name, 'wb')
        await file.__aenter__()
        with blob.open("rb") as blob_file:
            await file.write(await blob_file.read())
        return file


class GCSCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.Gcs

    def resolve(self, uri: Uri, config: GcsCollectConfig) -> Collector:
        config = GcsCollectConfig(
            bucket=bucket_name,
            credentials=credentials_info
        )
        return GCSCollector(config)
