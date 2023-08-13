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

def test_local_storage(temp_dir):
    storage = LocalFileStorage(temp_dir)
    uri = Uri("file://test.txt")
    payload = PutPayload(b"test")
    storage.put(uri, payload)
    assert Path(temp_dir, uri.path).exists()
    assert storage.get(uri).payload == b"test"
    storage.delete(uri)
    assert not Path(temp_dir, uri.path).exists()
