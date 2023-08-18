import asyncio
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.gcs.gcs_collector import GCSCollectorFactory
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend
import pytest


@pytest.fixture
def gcs_config():
    return {
        "bucket": "your_bucket_name",
        "credentials_path": "/path/to/your/credentials.json",
    }


def test_gcs_collector_factory():
    factory = GCSCollectorFactory()
    assert factory.backend() == CollectorBackend.Gcs

# Modify this function to test the GCS collector


async def test_gcs_collector(gcs_config):
    uri = Uri("gcs://" + gcs_config["bucket"] + "/prefix/")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri)
    assert collector is not None

    await collector.connect()

    async def poll_and_print():
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None

    # Modify this function to add files to your GCS bucket
    async def add_files():
        # Add files to your GCS bucket here
        pass

    async def main():
        await asyncio.gather(add_files(), poll_and_print())

    asyncio.run(main())


if __name__ == "__main__":
    # Modify this line to call the appropriate test function
    pytest.main(["-k", "test_gcs_collector"])
