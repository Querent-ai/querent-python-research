import asyncio
import tempfile
from pathlib import Path
import pytest
from querent.storage.local.local_file_storage import (
    LocalFileStorage,
    LocalStorageFactory,
)
from querent.common.uri import Uri
import querent.storage.payload as querent_payload
from querent.storage.storage_resolver import StorageResolver


@pytest.fixture
def temp_dir():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


def test_local_storage(temp_dir):
    uri = Uri("file://" + temp_dir)  # Use the temp_dir as the base URI
    storage = LocalFileStorage(uri, Path(temp_dir))  # Provide the 'uri' argument only
    payload = querent_payload.BytesPayload(b"test")

    print(f"Temp dir: {temp_dir}")
    print(f"URI: {uri}")

    # Put the payload
    asyncio.run(storage.put(Path(temp_dir + "/test.txt"), payload))
    file_path = Path(temp_dir, "test.txt")
    print(f"File path: {file_path}")

    assert file_path.exists()
    with open(file_path, "rb") as file:
        content = file.read()
        print(f"File content: {content.decode('utf-8')}")
        assert content == b"test"


def test_storage_resolver(temp_dir):
    uri = Uri("file://" + temp_dir)  # Use the temp_dir as the base URI
    resolver = StorageResolver()

    storage = asyncio.run(resolver.resolve(uri))

    payload = querent_payload.BytesPayload(b"ok testing")
    asyncio.run(storage.put(Path(temp_dir + "/test.txt"), payload))

    file_path = Path(temp_dir, "test.txt")
    assert file_path.exists()

    with open(file_path, "rb") as file:
        content = file.read()
        assert content == b"ok testing"
