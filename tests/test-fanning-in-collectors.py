import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid

num_dir = 0


@pytest.mark.asyncio
async def test_collect_and_ingest_pdf():
    # Set up the collector
    output_queue = asyncio.Queue()
    health_event = asyncio.Queue()
    stop_event = asyncio.Event()
    directories = ["./tests/data/pdf/", "./tests/data/pdf2/", "./tests/data/pdf3/"]
    workers = [
        create_workers(i, output_queue, health_event, stop_event) for i in directories
    ]

    stop_event_tasks = asyncio.create_task(stop_workers(stop_event, output_queue))
    health_event_tasks = asyncio.create_task(health_workers(health_event))
    queue_tasks = asyncio.create_task(see_contents(output_queue))
    await asyncio.gather(*workers, stop_event_tasks, len(directories))
    await queue_tasks


async def see_contents(output_queue):
    data = await output_queue.get()
    print(data)


async def stop_workers(stop_event: asyncio.Event, output_queue: asyncio.Queue):
    if output_queue.qsize == 50:
        stop_event.set()


async def health_workers(health_event):
    while True:
        data = await health_event.get()
        print(data)


async def create_workers(directory, output_queue, logger_event, stop_event):
    try:
        while not stop_event.is_set():
            collector_factory = FSCollectorFactory()
            uri = Uri("file://" + str(Path(directory).resolve()))
            config = FSCollectorConfig(root_path=uri.path, id=str(uuid.uuid4()))
            collector = collector_factory.resolve(uri, config)

            # Set up the ingestor
            ingestor_factory_manager = IngestorFactoryManager()
            ingestor_factory = await ingestor_factory_manager.get_factory("pdf")
            ingestor = await ingestor_factory.create("pdf", [])

            # Collect and ingest the PDF
            ingested_call = ingestor.ingest(collector.poll())
            async for ingested in ingested_call:
                if (
                    ingested.data is None
                    or ingested.data == ""
                    or ingested.error is not None
                ):
                    logger_event.put(f"Failure in polling {directory}'s files")
                    stop_event.set()
                print("ingested data   ", ingested.data)
                await output_queue.put(ingested.data)

            await output_queue.put("")
            logger_event.put(f"{directory} is running healthy")

    finally:
        # Always ensure we send the "DONE" signal, even if an exception occurred
        await output_queue.put("DONE")


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_pdf())
