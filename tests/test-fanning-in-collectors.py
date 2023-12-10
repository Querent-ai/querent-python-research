import asyncio
from pathlib import Path
from querent.collectors.fs.fs_collector import FSCollectorFactory
from querent.config.collector.collector_config import FSCollectorConfig
from querent.common.uri import Uri
from querent.ingestors.ingestor_manager import IngestorFactoryManager
import pytest
import uuid

count = 0


@pytest.mark.asyncio
async def test_collect_and_ingest_pdf():
    # Set up the collector
    output_queue = asyncio.Queue()
    logger_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    directories = ["./tests/data/pdf/", "./tests/data/pdf2/", "./tests/data/pdf3/"]
    workers = [
        create_workers(i, output_queue, logger_queue, stop_event) for i in directories
    ]

    # stop_event_tasks = asyncio.create_task(stop_workers(logger_queue, stop_event))
    queue_tasks = asyncio.create_task(see_contents(output_queue))
    asyncio.gather(*workers)
    await output_queue.join()
    await queue_tasks


async def see_contents(output_queue):
    while True:
        data = await output_queue.get()
        if data == "DONE":
            global count
            count = count + 1
        if count == 3:
            break
        else:
            output_queue.task_done()
            print(data)


async def create_workers(directory, output_queue, logger_queue, stop_event):
    try:
        collector_factory = FSCollectorFactory()
        uri = Uri("file://" + str(Path(directory).resolve()))
        config = FSCollectorConfig(root_path=uri.path, id=str(uuid.uuid4()))
        collector = collector_factory.resolve(uri, config)
        ingestor_factory_manager = IngestorFactoryManager()
        ingestor_factory = await ingestor_factory_manager.get_factory("pdf")
        ingestor = await ingestor_factory.create("pdf", [])
        ingested_call = ingestor.ingest(collector.poll())
        async for ingested in ingested_call:
            if ingested.data is None:
                # continue
                await logger_queue.put("1 file received")
                print("Putting 1 file in logger queue")
            else:
                await output_queue.put(ingested.data)
    except Exception as e:
        print("Got an exception:  ", e)

    finally:
        # Always ensure we send the "DONE" signal, even if an exception occurred
        await output_queue.put("DONE")


if __name__ == "__main__":
    asyncio.run(test_collect_and_ingest_pdf())
