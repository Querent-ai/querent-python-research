import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest


@pytest.mark.asyncio
async def test_collect_and_ingest_xlsx():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/xlsx/").resolve()))
    config = FSCollectorConfig(root_path=uri.path)
    collector = collector_factory.resolve(uri, config)

    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("xlsx")
    ingestor = await ingestor_factory.create("xlsx", [])

    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            for i in range(0, ingested.shape[0]):
                counter += 1
        assert counter == 3

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_xlsx())
