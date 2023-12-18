import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import DriveCollectorConfig
from querent.common.uri import Uri
import uuid
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_message import MessageState, MessageType
import time
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def drive_config():
    return DriveCollectorConfig(
        id=str(uuid.uuid4()),
        drive_refresh_token=os.getenv("DRIVE_REFRESH_TOKEN"),
        drive_token=os.getenv("DRIVE_TOKEN"),
        drive_scopes=os.getenv("DRIVE_SCOPES"),
        chunk_size=1024 * 1024,
        drive_client_id=os.getenv("DRIVE_CLIENT_ID"),
        drive_client_secret=os.getenv("DRIVE_CLIENT_SECRET"),
        specific_file_type="application/pdf",
        # Remember to put id of the folder you want to crawl
        folder_to_crawl="1BtLKXcYBrS16CX0R4V1X7Y4XyO9Ct7f8",
    )


@pytest.mark.asyncio
async def test_google_drive_collector_signal(drive_config):
    uri = Uri("drive://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, drive_config)
    assert collector is not None
    await collector.connect()

    async def add_message(queue: QuerentQueue):
        time.sleep(5)
        message = MessageState(
            message_type=MessageType.STOP, timestamp=time.time(), payload=None
        )

        await queue.put(message)

    # message_task = asyncio.create_task(add_message(collector.message_queue))

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert result is not None
            chunk = result.unwrap()
            if chunk is not None:
                counter += 1
        assert counter == 16

    asyncio.gather(
        poll_and_print(), asyncio.create_task(add_message(collector.message_queue))
    )


if __name__ == "__main__":
    asyncio.run(test_google_drive_collector_signal())
