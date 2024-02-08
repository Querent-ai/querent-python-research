from typing import AsyncGenerator
import io

from azure.storage.blob import BlobServiceClient
from querent.common.types.collected_bytes import CollectedBytes
from querent.config.collector.collector_config import CollectorBackend, AzureCollectConfig
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.uri import Uri
from querent.logging.logger import setup_logger


class AzureCollector(Collector):
    def __init__(self, config: AzureCollectConfig):
        self.connection_string = config.connection_string
        self.account_url = config.account_url
        self.credentials = config.credentials
        self.container_name = config.container
        self.chunk_size = 1024  # Default value
        if config.chunk_size and config.chunk_size.isdigit():
            self.chunk_size = int(config.chunk_size)
        self.prefix = config.prefix
        self.blob_service_client = None
        self.container_client = None
        self.logger = setup_logger(__name__, "AzureCollector")

    async def connect(self):
        try:
            if self.connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    conn_str=self.connection_string,
                    credential=self.credentials,
                )
            elif self.account_url:
                self.blob_service_client = BlobServiceClient(
                    account_url=self.account_url,
                    credential=self.credentials,
                )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
        except Exception as e:
            self.logger.error(f"Error connecting to Azure Blob Storage: {e}")
            raise e

    async def disconnect(self):
        pass  # No asynchronous disconnect needed for the Azure Blob Storage client

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        try:
            if not self.container_client:
                await self.connect()

            blob_list = self.container_client.list_blobs(name_starts_with=self.prefix)
            for blob in blob_list:
                file = self.download_blob_as_byte_stream(
                    self.container_client, blob.name
                )
                async for chunk in self.read_chunks(file):
                    yield CollectedBytes(file=blob.name, data=chunk, error=None)
                yield CollectedBytes(file=blob.name, data=None, error=None, eof=True)
        except Exception as e:
            # Handle exceptions gracefully, e.g., log the error
            self.logger.error(f"Error polling Azure Blob Storage: {e}")
            raise e
        finally:
            # Disconnect the client when done
            await self.disconnect()

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
        return AzureCollector(config)
