import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.common import common_errors
import pytest
import uuid


@pytest.mark.asyncio
async def test_collect_and_ingest_wrong_txt():
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/image/").resolve()))
    config = FSCollectorConfig(root_path=uri.path, id=str(uuid.uuid4()))
    collector = collector_factory.resolve(uri, config)

    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("html")
    ingestor = await ingestor_factory.create("html", [])

    ingested_call = ingestor.ingest(collector.poll())

    async def poll_and_print():
        with pytest.raises(common_errors.UnicodeDecodeError):
            async for ingested in ingested_call:
                if ingested.data is None:
                    continue

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_wrong_txt())
