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
    print("Setting up tasks")
    output_queue = asyncio.Queue()
    logger_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    directories = ["./tests/data/pdf/", "./tests/data/pdf2/", "./tests/data/pdf3/"]
    
    workers = [create_workers(i, output_queue, logger_queue, stop_event) for i in directories]
    stop_event_task = asyncio.create_task(stop_workers(logger_queue, stop_event))
    queue_task = asyncio.create_task(see_contents(output_queue))

    print("Starting asyncio.gather")
    await asyncio.gather(*workers, stop_event_task, queue_task)
    print("All tasks completed")
async def see_contents(output_queue):
    while True:
        data = await output_queue.get()
        if data == "DONE":
            break
        # print(data)
async def stop_workers(logger_queue: asyncio.Queue, stop_event: asyncio.Event):
    while True:
        if logger_queue.qsize() >= 3:
            stop_event.set()
            print("Worker stopped")
            break
        await asyncio.sleep(1)
async def create_workers(directory, output_queue, logger_event, stop_event):
    try:
        print("Here")
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
                if ingested is None or ingested.data is None:
                    print(f"No data or None object found in a file in {directory}")
                    continue
                print(f"File processed in {directory}: {ingested.data}")
                await logger_event.put("1 file received")
                await output_queue.put(ingested.data)
            if stop_event.is_set():
                print(f"Stopping worker for directory: {directory} due to stop event")
                break

        print(f"Worker completed for directory: {directory}")
    except Exception as e:
        print(f"Error in worker for {directory}: {e}")
    finally:
        await output_queue.put("DONE")
if __name__ == "__main__":
    print("Starting main")
    asyncio.run(test_collect_and_ingest_pdf())
    print("Main completed")