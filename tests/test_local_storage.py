import tempfile
from pathlib import Path
import pytest
from querent.storage.local.local_storage import LocalFileStorage
from querent.common.uri import Uri
from querent.storage.payload import PutPayload

@pytest.fixture
def temp_dir():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()

@pytest.mark.asyncio
async def test_put(temp_dir):
    uri = Uri("file:///path/to/storage")
    storage = LocalFileStorage(uri, Path(temp_dir))
    payload = PutPayload(b"test content")

    # Test put method
    await storage.put(Path("test.txt"), payload)
    file_path = Path(temp_dir) / "test.txt"
    assert file_path.exists()
    with open(file_path, "rb") as file:
        content = file.read()
        assert content == b"test content"
