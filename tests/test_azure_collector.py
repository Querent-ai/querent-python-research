import asyncio

from querent.config.collector_config import AzureCollectConfig
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.azure.azure_collector import AzureCollectorFactory
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
azure_account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
azure_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")


@pytest.fixture
def azure_config():
    config = AzureCollectConfig(
        connection_string="",
        account_url=azure_account_url,
        credentials=azure_account_key,
        chunk=1024,
        container="testfiles",
        prefix="",
    )
    return config


def test_azure_collector_factory():
    factory = AzureCollectorFactory()
    assert factory.backend() == CollectorBackend.AzureBlobStorage


# Modify this function to test the Azure collector


@pytest.mark.asyncio
async def test_azure_collector(azure_config):
    config = azure_config
    uri = Uri("azure://" + config.container)
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, config)
    assert collector is not None

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk:
                counter += 1
        assert counter == 1433

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_azure_collector())
