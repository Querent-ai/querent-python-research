import asyncio
from pathlib import Path
import tempfile
from querent.collectors.collector_resolver import CollectorResolver
from querent.collectors.fs.fs_collector import FSCollectorFactory
import pytest

from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, FSCollectorConfig


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


def test_fs_collector(temp_dir):
    uri = Uri("file://" + temp_dir)
    resolver = CollectorResolver()
    fileConfig = FSCollectorConfig(root_path=uri.path)
    collector = resolver.resolve(uri, fileConfig)
    assert collector is not None


def test_fs_collector_factory():
    factory = FSCollectorFactory()
    assert factory.backend() == CollectorBackend.LocalFile


async def poll_and_print(collector):
    async for result in collector.poll():
        assert not result.is_error()
        chunk = result.unwrap()
        assert chunk is not None


async def add_files(temp_dir):
    file_path = Path(temp_dir, "test_temp.txt")
    with open(file_path, "wb") as file:
        file.write(b"test_add_files_read_via_collector")


async def main():
    temp_dir = tempfile.TemporaryDirectory()
    uri = Uri("file://" + temp_dir.name)
    resolver = CollectorResolver()
    fileConfig = FSCollectorConfig(root_path=uri.path)
    collector = resolver.resolve(uri, fileConfig)
    assert collector is not None

    await add_files(temp_dir.name)
    await poll_and_print(collector)

    temp_dir.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
