import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest


@pytest.mark.asyncio
async def test_collect_and_ingest_jpg():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/image/").resolve()))
    config = FSCollectorConfig(root_path=uri.path)
    collector = collector_factory.resolve(uri, config)

    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("png")
    ingestor = await ingestor_factory.create("jpg", [])

    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if len(ingested) == 0:
                counter += 1
        assert counter == 1

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_jpg())