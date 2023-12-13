import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid


@pytest.mark.asyncio
async def test_collect_and_ingest_code():
    # Set up the collector
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/code/").resolve()))
    config = FSCollectorConfig(root_path=uri.path, id=str(uuid.uuid4()))
    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory("py")
    ingestor = await ingestor_factory.create("py", [])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested.data != "" or ingested is not None:
                print(ingested)
                counter += 1
        # counter is 2 though files are 4, that is because we are yielding an empty IngestedCode at the end of each file
        assert counter == 4

    await poll_and_print()


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_code())
