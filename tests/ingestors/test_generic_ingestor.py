import asyncio
import os
from pathlib import Path
from querent.collectors.slack.slack_collector import SlackCollectorFactory
from querent.config.collector.collector_config import SlackCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid

from dotenv import load_dotenv

load_dotenv()


def get_collector_config():
    return SlackCollectorConfig(
        id=str(uuid.uuid4()),
        channel_name="C05TA5R7D88",
        cursor=None,
        include_all_metadata=0,
        inclusive=0,
        latest=0,
        limit=100,
        access_token=os.getenv("SLACK_ACCESS_KEY"),
    )


@pytest.mark.asyncio
async def test_collect_and_ingest_generic_bytes():
    # Set up the collector
    collector_factory = SlackCollectorFactory()
    uri = Uri("slack://")
    config = get_collector_config()
    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("slack")
    ingestor = await ingestor_factory.create("slack", [])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested is not "" or ingested is not None:
                counter += 1
        # Changing the number because messages before 90 days get deleted from slack
        assert counter > 0


    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_generic_bytes())
