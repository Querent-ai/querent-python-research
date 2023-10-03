import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest


@pytest.mark.asyncio
async def test_collect_and_ingest_txt():
    # Set up the collector
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/text/").resolve()))
    config = FSCollectorConfig(root_path=uri.path)
    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("txt")
    ingestor = await ingestor_factory.create("txt", [])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested is not "" or ingested is not None:
                counter += 1
        assert counter == 15

    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_txt())
