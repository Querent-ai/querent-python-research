import asyncio
from asyncio import Queue
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid


@pytest.mark.asyncio
async def test_ingest_all_async():
    # Set up the collectors
    directories = ["./tests/data/pdf/", "./tests/data/pdf2/", "./tests/data/pdf3/"]
    collectors = [
        FSCollectorFactory().resolve(
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
    while not result_queue.empty():
        ingested_data = await result_queue.get()
        if ingested_data is not None:
            unique_files.add(ingested_data.file)
            counter += 1
    assert counter == 91
    assert len(unique_files) == 6


if __name__ == "__main__":
    asyncio.run(test_ingest_all_async())
