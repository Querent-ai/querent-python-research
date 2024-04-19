import asyncio
from pathlib import Path
import pytest
import os
import uuid
from dotenv import load_dotenv

from querent.config.collector.collector_config import (
    FSCollectorConfig,
    DriveCollectorConfig,
    SlackCollectorConfig,
)
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.types.ingested_tokens import IngestedTokens


load_dotenv()


def drive_config():
    return DriveCollectorConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "drive_refresh_token": os.getenv("DRIVE_REFRESH_TOKEN"),
            "drive_token": os.getenv("DRIVE_TOKEN"),
            "drive_scopes": os.getenv("DRIVE_SCOPES"),
            "chunk_size": "1048576",
            "drive_client_id": os.getenv("DRIVE_CLIENT_ID"),
            "drive_client_secret": os.getenv("DRIVE_CLIENT_SECRET"),
            "specific_file_type": "application/pdf",
            "folder_to_crawl": "1BtLKXcYBrS16CX0R4V1X7Y4XyO9Ct7f8",
            "name": "Drive-config",
            "config": {},
            "uri": "drive://",
        }
    )


def slack_config():
    return SlackCollectorConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "channel_name": "C05TA5R7D88",
            "cursor": None,
            "include_all_metadata": 0,
            "inclusive": 0,
            "latest": "0",
            "limit": 100,
            "access_token": os.getenv("SLACK_ACCESS_KEY"),
            "name": "Slack-config",
            "config": {},
            "uri": "slack://",
        }
    )


@pytest.mark.asyncio
async def test_multiple_collectors_all_async():
    # Set up the collectors
    directories = ["./tests/data/pdf/", "./tests/data/pdf2/", "./tests/data/pdf3/"]
    collectors = [
        CollectorResolver().resolve(
            Uri("file://" + str(Path(directory).resolve())),
            FSCollectorConfig(
                config_source={
                    "id": str(uuid.uuid4()),
                    "root_path": directory,
                    "name": "Local-config",
                    "config": {},
                    "uri": "file://",
                }
            ),
        )
        for directory in directories
    ]

    collectors.append(
        CollectorResolver().resolve(
            Uri("drive://"),
            drive_config(),
        )
    )

    collectors.append(
        CollectorResolver().resolve(
            Uri("slack://"),
            slack_config(),
        )
    )

    for collector in collectors:
        await collector.connect()

    # Set up the result queue
    result_queue = asyncio.Queue()

    # Create the IngestorFactoryManager
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    # Start the ingest_all_async in a separate task
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    # Wait for the task to complete
    await asyncio.gather(ingest_task)

    # Optionally, check the result_queue for ingested data
    counter = 0
    unique_files = set()
    messages = 0
    while not result_queue.empty():
        ingested_data = await result_queue.get()
        if ingested_data is not None:
            if (
                isinstance(ingested_data, IngestedTokens)
                and ingested_data.is_token_stream
            ):
                messages += 1
            counter += 1
    assert counter == 85
    assert messages > 0


if __name__ == "__main__":
    asyncio.run(test_multiple_collectors_all_async())
