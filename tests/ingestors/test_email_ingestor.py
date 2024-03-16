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

from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.processors.text_processor import TextProcessor

load_dotenv()


@pytest.fixture
def email_config():
    return EmailCollectorConfig(
        config_source={
            "backend": "email",
            "id": str(uuid.uuid4()),
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "imap_folder": "[Gmail]/Drafts",
            "imap_certfile": None,
            "imap_keyfile": None,
            "name": "Email-config",
            "config": {},
            "uri": "email://",
        }
    )


@pytest.mark.asyncio
async def test_email_ingestor(email_config):
    uri = Uri("email://")
    resolver = CollectorResolver()
    collector = resolver.resolve(uri, email_config)
    assert collector is not None
    await collector.connect()
    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("email")
    processor = TextProcessor()
    ingestor = await ingestor_factory.create("email", [processor])
    ingested_call = ingestor.ingest(collector.poll())

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested != "" or ingested is not None:
                print(ingested)
                counter += 1
        assert counter == 4

    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_email_ingestor())
