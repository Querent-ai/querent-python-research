import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid


@pytest.mark.asyncio
async def test_collect_and_ingest_json_data():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/json/").resolve()))
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

    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("json")
    ingestor = await ingestor_factory.create("json", [])

    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            assert ingested.error is None
            assert ingested.file is not None
            counter += 1
        # 2 extra IngestedTokens is to signify end of file
        assert counter == 4

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_json_data())
