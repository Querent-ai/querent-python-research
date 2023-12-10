import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import DropboxConfig
from querent.common.uri import Uri
import uuid

from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def dropbox_config():
    return DropboxConfig(
        id=str(uuid.uuid4()),
        dropbox_app_key=os.getenv("DROPBOX_APP_KEY"),
        dropbox_app_secret=os.getenv("DROPBOX_APP_SECRET"),
        dropbox_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN"),
        folder_path="",
        chunk_size=1024,
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

            if chunk is not None:
                counter += 1
        assert counter == 170

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_dropbox_collector())
