import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector_config import DropboxConfig
from querent.common.uri import Uri

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def dropbox_config():
    return DropboxConfig(
        access_token=os.getenv("DROPBOX_ACCESS_TOKEN"), folder_path="", chunk_size=1024
    )


@pytest.mark.asyncio
async def test_dropbox_collector(dropbox_config):
    uri = Uri("dropbox://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, dropbox_config)
    assert collector is not None

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk != "" or chunk is not None:
                counter += 1
        assert counter == 170

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_dropbox_collector())
