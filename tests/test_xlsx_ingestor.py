import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.common.types.ingested_tokens import IngestedTokens
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
        nonlocal counter  # Use nonlocal to modify the outer counter variable
        async for ingested in ingested_call:
            assert ingested is not None
            assert isinstance(ingested, IngestedTokens)
            assert ingested.error is None
            assert ingested.file is not None
            assert ingested.data is not None
            assert len(ingested.data) > 0
            counter += 1
        assert counter == 1

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_xlsx())
