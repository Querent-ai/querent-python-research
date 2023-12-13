import asyncio
import pytest
import os
from querent.collectors.collector_resolver import CollectorResolver
from querent.config.collector.collector_config import (
    CollectorBackend,
    EmailCollectorConfig,
)
from querent.common.uri import Uri
import uuid
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def email_config():
    return EmailCollectorConfig(
        backend=CollectorBackend.Email,
        id=str(uuid.uuid4()),
        imap_server="imap.gmail.com",  # "imap.gmail.com
        imap_port=993,
        imap_username="puneet@querent.xyz",
        imap_password=os.getenv("IMAP_PASSWORD"),
        imap_folder="[Gmail]/Drafts",
        imap_certfile=None,
        imap_keyfile=None,
    )


@pytest.mark.asyncio
async def test_email_collector(email_config):
    uri = Uri("email://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, email_config)
    assert collector is not None
    await collector.connect()

    async def poll_and_print():
        counter = 0
        async for result in collector.poll():
            assert result is not None
            chunk = result.unwrap()

            if chunk is not None:
                counter += 1
        assert counter == 2

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_email_collector())
