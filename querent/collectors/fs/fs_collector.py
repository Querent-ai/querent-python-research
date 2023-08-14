import asyncio
from pathlib import Path
from typing import AsyncGenerator
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.collectors.collector_result import CollectorResult
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, FSCollectorConfig


class FSCollector(Collector):
    def __init__(self, config: FSCollectorConfig):
        self.root_dir = Path(config.root_path)
        self.chunk_size = config.chunk_size

    async def connect(self):
        # Add your setup logic here if needed
        pass

    async def disconnect(self):
        # Add your cleanup logic here if needed
        pass

    async def poll(self) -> AsyncGenerator[CollectorResult, None]:
        for file_path in self.walk_files(self.root_dir):
            async with file_path.open("rb") as file:
                async for chunk in self.read_chunks(file):
                    yield CollectorResult(file_path, chunk)

    async def read_chunks(self, file):
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk

    async def walk_files(self, root: Path):
        for dir_path, _, filenames in root.iterdir():
            for filename in filenames:
                yield Path(dir_path) / filename


class FSCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.LocalFile

    def resolve(self, uri: Uri) -> Collector:
        config = FSCollectorConfig(root_path=uri.path)
        return FSCollector(config)


# Test Case
async def test_fs_collector():
    root_dir = Path("test_files")
    collector = FSCollector(root_dir)

    async def poll_and_print():
        async for result in collector.poll():
            print(result)

    await collector.connect()
    await poll_and_print()
    await collector.disconnect()


if __name__ == "__main__":
    asyncio.run(test_fs_collector())
