import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest


@pytest.mark.asyncio
async def test_collect_and_ingest_wrong_image_bytes():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/html/").resolve()))
    config = FSCollectorConfig(root_path=uri.path)
    collector = collector_factory.resolve(uri, config)

    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("jpg")
    ingestor = await ingestor_factory.create("jpg", [])

    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            if ingested.data is None:
                continue
            if len(ingested.data) != 0:
                counter += 1
        # Counter would be zero as we are not able to open the given image file
        assert counter == 0

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_wrong_image_bytes())
