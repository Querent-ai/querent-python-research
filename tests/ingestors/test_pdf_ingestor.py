import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
from querent.processors.text_processor import TextProcessor
from querent.common.types.ingested_images import IngestedImages
import pytest
import uuid


@pytest.mark.asyncio
async def test_collect_and_ingest_pdf():
    # Set up the collector
    collector_factory = FSCollectorFactory()
    uri = Uri("file://" + str(Path("./tests/data/pdf/").resolve()))
    config = FSCollectorConfig(root_path=uri.path, id=str(uuid.uuid4()))
    collector = collector_factory.resolve(uri, config)

    # Set up the ingestor
    ingestor_factory_manager = IngestorFactoryManager()
    ingestor_factory = await ingestor_factory_manager.get_factory(
        "pdf"
    )  # Notice the use of await here
    processor = TextProcessor()
    ingestor = await ingestor_factory.create("pdf", [processor])

    # Collect and ingest the PDF
    ingested_call = ingestor.ingest(collector.poll())
    counter = 0

    async def poll_and_print():
        counter = 0
        async for ingested in ingested_call:
            assert ingested is not None
            if ingested is not "" or ingested is not None:
                counter += 1
                if isinstance(ingested, IngestedImages):
                    print(ingested.page_num)
        assert (
            counter == 31
        )  # 30 pages in the PDF and 1 empty IngestedTokens to signify end of file

    await poll_and_print()  # Notice the use of await here


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_pdf())
