import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector_config import DriveCollectorConfig
from querent.common.uri import Uri
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def drive_config():
    return DriveCollectorConfig(
        drive_refresh_token=os.getenv("DRIVE_REFRESH_TOKEN"),
        drive_token=os.getenv("DRIVE_TOKEN"),
        drive_scopes=os.getenv("DRIVE_SCOPES"),
        chunk_size=1024 * 1024,
    )


@pytest.mark.asyncio
async def test_google_drive_collector(drive_config):
    uri = Uri("drive://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, drive_config)
    assert collector is not None
    await collector.connect()

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert not result.is_error()
            chunk = result.unwrap()
            assert chunk is not None
            if chunk != "" or chunk is not None:
                counter += 1
        print(counter)

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_google_drive_collector())
