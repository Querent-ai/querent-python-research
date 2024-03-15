"""Test cases for audio ingestors"""
from pathlib import Path
import pytest
import asyncio

from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import uuid

from querent.processors.text_cleanup_processor import TextCleanupProcessor


@pytest.mark.asyncio
async def test_collect_and_ingest_audio():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/video/").resolve()))
    config = FSCollectorConfig(
        config_source={
            "id": str(uuid.uuid4()),
            "root_path": uri.path,
            "name": "Local-config",
            "config": {},
            "uri": "file://",
        }
    )
    collector = collector_factory.resolve(uri, config)
    text_cleanup_processor = TextCleanupProcessor()
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("mp4")
    ingestor = await ingestor_factory.create("mp4", processors=[text_cleanup_processor])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested.error is None
            assert ingested.file is not None
            counter += 1

        # counter is 2 because at the end of each file there is an empty IngestedTokens being yielded
        assert counter >0

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_audio())
