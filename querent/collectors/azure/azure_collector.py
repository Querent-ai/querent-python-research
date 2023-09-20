import asyncio
from typing import AsyncGenerator
import io

from azure.storage.blob import BlobServiceClient
from querent.config.collector_config import CollectorBackend, AzureCollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri


class AzureCollector(Collector):
    def __init__(self, config: AzureCollectConfig, container_name: str, prefix: str):
        self.account_url = config["account_url"]
        self.blob_service_client = BlobServiceClient(
            account_url=self.account_url, credential=config["credential"]
        )
        self.container_name = container_name
        self.chunk_size = 1024
        self.prefix = prefix

    async def connect(self):
        pass  # No asynchronous connection needed for the Azure Blob Storage client

    async def disconnect(self):
        pass  # No asynchronous disconnect needed for the Azure Blob Storage client

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        async for blob in container_client.list_blobs(name_starts_with=self.prefix):
            file = self.download_blob_as_byte_stream(container_client, blob.name)
            async for chunk in self.read_chunks(file):
                yield CollectorResult({"object_key": blob.name, "chunk": chunk})

    async def read_chunks(self, file):
        while True:
            chunk = file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    def download_blob_as_byte_stream(self, container_client, blob_name):
        blob_client = container_client.get_blob_client(blob_name)
        blob_properties = blob_client.get_blob_properties()
        byte_stream = io.BytesIO()

        if blob_properties["size"] > 0:
            stream = blob_client.download_blob()
            byte_stream.write(stream.readall())
            byte_stream.seek(0)  # Rewind the stream to the beginning

        return byte_stream


class AzureCollectorFactory(CollectorFactory):
    def backend(self) -> CollectorBackend:
        return CollectorBackend.AzureBlobStorage

    def resolve(self, uri: Uri, config: AzureCollectConfig) -> Collector:
        container_name = uri.path.strip("/")
        prefix = uri.query.get("prefix", "")
        return AzureCollector(config, container_name, prefix)
