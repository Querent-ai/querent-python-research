import os
import tempfile
import shutil
import asyncio
from pathlib import Path
from typing import Union
from querent.storage.storage_base import Storage
from querent.storage.put_payload import PutPayload
from querent.storage.storage_errors import StorageError, StorageErrorKind
from querent.common.uri import Uri
from querent.config.storage_config import StorageBackend
from querent.storage.storage_factory import StorageFactory
from asyncio.futures import Future
from typing import Optional, Dict, Tuple
from querent.storage.debounced_storage import DebouncedStorage
import concurrent.futures


class LocalFileStorage(Storage):
    def __init__(self, uri: Uri, root: Path):
        self.uri = uri
        self.root = root

    def full_path(self, relative_path: Path) -> Path:
        self.ensure_valid_relative_path(relative_path)
        return self.root / relative_path

    @staticmethod
    def ensure_valid_relative_path(path: Path):
        for component in path.parts:
            if component == "..":
                raise StorageError(
                    StorageErrorKind.Unauthorized,
                    f"Path '{path}' is forbidden. Only simple relative paths are allowed.",
                )

    async def check_connectivity(self) -> None:
        if not self.root.exists():
            try:
                os.makedirs(self.root)
            except Exception as e:
                raise StorageError(
                    StorageErrorKind.ConnectionError,
                    f"Failed to create directories at {self.root}: {e}",
                )

    async def put(self, path: Path, payload: PutPayload) -> None:
        full_path = self.full_path(path)
        parent_dir = full_path.parent
        try:
            os.makedirs(parent_dir, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=parent_dir, delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.close()
                await asyncio.to_thread(shutil.copyfileobj, payload.byte_stream(), temp_path)
                os.rename(temp_path, full_path)
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to write file to {full_path}: {e}",
            )

    async def delete_single_file(self, relative_path: Path) -> None:
        full_path = self.full_path(relative_path)
        try:
            os.remove(full_path)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to delete file {full_path}: {e}",
            )

    async def delete(self, path: Path) -> None:
        await self.delete_single_file(path)
        parent = path.parent
        while parent != self.root and not any(parent.iterdir()):
            try:
                os.rmdir(parent)
            except OSError:
                break
            parent = parent.parent

    async def bulk_delete(self, paths: [Path]) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_path = {executor.submit(self.delete_single_file, path): path for path in paths}
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

    async def get_all(self, path: Path) -> bytes:
        full_path = self.full_path(path)
        try:
            with open(full_path, "rb") as file:
                content = file.read()
                return content
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to read file from {full_path}: {e}",
            )

    def uri(self) -> Uri:
        return self.uri


class LocalFileStorageFactory(StorageFactory):
    def backend(self) -> StorageBackend:
        return StorageBackend.LocalFile

    async def resolve(self, uri: Uri) -> Storage:
        root = uri.filepath()
        return DebouncedStorage(LocalFileStorage(uri, root))


if __name__ == "__main__":
    uri_str = "file:///path/to/storage"
    uri = Uri(uri_str)
    storage = LocalFileStorageFactory().resolve(uri)
    storage.check_connectivity()
