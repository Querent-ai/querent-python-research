import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.processors.text_cleanup_processor import TextCleanupProcessor
import pytest
import uuid


@pytest.mark.asyncio
async def test_collect_and_ingest_xml():
    # Set up the collector
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/xml/").resolve()))
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

    # Set up the ingestor
    text_cleanup_processor = TextCleanupProcessor()
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("xml")
    ingestor = await ingestor_factory.create("xml", processors=[text_cleanup_processor])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            if ingested != "" or ingested is not None:
                counter += 1
        # 2 extra empty Ingested Tokens signfying end of file
        assert counter == 4

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_xml())
