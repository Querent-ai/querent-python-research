from pathlib import Path
from functools import lru_cache
import asyncio
from asyncio import Lock
import tempfile
import shutil
from querent.common.uri import Protocol, Uri
from querent.config.storage_config import StorageBackend

from querent.storage.storage_errors import StorageError, StorageErrorKind
from querent.storage.storage_base import Storage
from querent.storage.storage_factory import StorageFactory

class AsyncDebouncer:
    def __init__(self):
        self.cache = {}

    def len(self):
        return len(self.cache)

    def cleanup(self):
        self.cache = {k: v for k, v in self.cache.items() if v.future.done()}

    async def get_or_create(self, key, build_a_future):
        self.cleanup()

        if key in self.cache:
            if self.cache[key].future.done():
                del self.cache[key]
            else:
                return await self.cache[key].future

        lock = Lock()
        async with lock:
            if key in self.cache:
                return await self.cache[key].future

            future = asyncio.create_task(build_a_future())
            self.cache[key] = DebouncerEntry(future)
            result = await future
            del self.cache[key]
            return result

class DebouncerEntry:
    def __init__(self, future):
        self.future = future

class DebouncedStorage:
    def __init__(self, underlying):
        self.underlying = underlying
        self.slice_debouncer = AsyncDebouncer()

    async def check_connectivity(self):
        return await self.underlying.check_connectivity()

    async def put(self, path, payload):
        await self.underlying.put(path, payload)

    async def copy_to(self, path, output):
        await self.underlying.copy_to(path, output)

    async def get_slice(self, path, range_):
        key = (path, range_)
        cached_result = await self.get_slice_cache(key)
        if cached_result is None:
            result = await self.underlying.get_slice(path, range_)
            await self.set_slice_cache(key, result)
            return result
        return cached_result

    @lru_cache(maxsize=128)
    def get_slice_cache(self, key):
        pass

    async def set_slice_cache(self, key, value):
        pass

    async def delete(self, path):
        await self.underlying.delete(path)

    async def bulk_delete(self, paths):
        await self.underlying.bulk_delete(paths)

    async def get_all(self, path):
        key = (path, 0, float('inf'))
        cached_result = await self.get_slice_cache(key)
        if cached_result is None:
            result = await self.underlying.get_all(path)
            await self.set_slice_cache(key, result)
            return result
        return cached_result

    async def file_num_bytes(self, path):
        return await self.underlying.file_num_bytes(path)

    def uri(self):
        return self.underlying.uri()

class LocalFileStorage(Storage):
    def __init__(self, uri, root):
        self.uri = uri
        self.root = root
        self.cache_lock = Lock()

    async def full_path(self, relative_path):
        await self.ensure_valid_relative_path(relative_path)
        return self.root / relative_path

    async def ensure_valid_relative_path(self, path):
        async with self.cache_lock:
            for component in path.parts:
                if component == "..":
                    raise StorageError(
                        StorageErrorKind.Unauthorized,
                        f"Path '{path}' is forbidden. Only simple relative paths are allowed.",
                    )

    async def check_connectivity(self):
        if not self.root.exists():
            try:
                self.root.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise StorageError(
                    StorageErrorKind.ConnectionError,
                    f"Failed to create directories at {self.root}: {e}",
                )

    async def put(self, path, payload):
        full_path = await self.full_path(path)
        parent_dir = full_path.parent
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=parent_dir, delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                temp_file.close()
                await asyncio.to_thread(shutil.copyfileobj, payload.byte_stream(), temp_path)
                temp_path.rename(full_path)
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to write file to {full_path}: {e}",
            )

    async def delete_single_file(self, relative_path):
        full_path = await self.full_path(relative_path)
        try:
            full_path.unlink()
        except FileNotFoundError:
            pass
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to delete file {full_path}: {e}",
            )

    async def delete(self, path):
        await self.delete_single_file(path)

class LocalStorageFactory(StorageFactory):
    def backend(self) -> StorageBackend:
        return StorageBackend.LocalFile

    async def resolve(self, uri: str) -> Storage:
        parsed_uri = Uri(uri)  # Ensure you have the Uri class imported and defined
        if parsed_uri.protocol == Protocol.File:
            root_path = Path(parsed_uri.path)
            return LocalFileStorage(uri, root_path)
        else:
            raise ValueError("Unsupported protocol")