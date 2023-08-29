import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest

async def test_collect_and_ingest_pdf():
    # Set up the collector
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/pdf/").resolve()))
    config = FSCollectorConfig(root_path=uri.path)
    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = ingestor_factory_manager.get_factory("pdf")
    ingestor = await ingestor_factory.create("pdf", [])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    async for ingested in ingested_call:
        print(ingested)


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_pdf())
