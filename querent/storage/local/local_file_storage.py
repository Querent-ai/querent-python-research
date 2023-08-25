from pathlib import Path
from functools import lru_cache
import asyncio
from asyncio import Lock
import tempfile
import shutil
from querent.common.uri import Protocol, Uri
from querent.config.storage_config import StorageBackend
from querent.storage.payload import PutPayload

from querent.storage.storage_errors import StorageError, StorageErrorKind
from querent.storage.storage_base import Storage
from querent.storage.storage_factory import StorageFactory
from querent.storage.storage_result import StorageResult


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
        key = (path, 0, float("inf"))
        cached_result = await self.get_slice_cache(key)
        if cached_result is None:
            result = await self.underlying.get_all(path)
            await self.set_slice_cache(key, result)
            return result
        return cached_result

    async def file_num_bytes(self, path):
        return await self.underlying.file_num_bytes(path)

    def get_uri(self):
        return self.underlying.get_uri()


class LocalFileStorage(Storage):
    def __init__(self, uri: Uri, root=None):
        self.uri = uri
        if not root:
            root = Path(uri.path)
        self.root = root
        self.cache_lock = Lock()

    async def initialize_lock(self):
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

    async def put(self, path: Path, payload: PutPayload) -> StorageResult:
        full_path = await self.full_path(path)
        parent_dir = full_path.parent
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
            payload_len = payload.len()
            if payload_len > 0:
                with open(full_path, "wb") as file:
                    for i in range(0, payload_len, 1024):
                        chunk = await payload.range_byte_stream(i, i + 1024)
                        file.write(chunk)
            return StorageResult.success(None)
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to write file {full_path}: {e}",
            )

    async def copy_to(self, path, output) -> StorageResult:
        full_path = await self.full_path(path)
        with open(full_path, "rb") as file:
            await asyncio.to_thread(shutil.copyfileobj, file, output)
        return StorageResult.success(None)

    async def get_slice(self, path, start, end) -> StorageResult:
        full_path = await self.full_path(path)
        with open(full_path, "rb") as file:
            file.seek(start)
            return StorageResult.success(file.read(end - start))

    async def get_all(self, path) -> StorageResult:
        full_path = await self.full_path(path)
        with open(full_path, "rb") as file:
            return StorageResult.success(file.read())

    async def delete(self, path) -> StorageResult:
        full_path = await self.full_path(path)
        try:
            full_path.unlink()
            return StorageResult.success(None)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise StorageError(
                StorageErrorKind.Io,
                f"Failed to delete file {full_path}: {e}",
            )

    async def bulk_delete(self, paths):
        for path in paths:
            await self.delete(path)

    async def exists(self, path) -> StorageResult:
        full_path = await self.full_path(path)
        return StorageResult.success(full_path.exists())

    async def file_num_bytes(self, path) -> StorageResult:
        full_path = await self.full_path(path)
        try:
            return StorageResult.success(full_path.stat().st_size)
        except FileNotFoundError:
            raise StorageError(
                StorageErrorKind.NotFound,
                f"File {full_path} not found",
            )

    @property
    def get_uri(self) -> Uri:
        return self.uri


class LocalStorageFactory(StorageFactory):
    def backend(self) -> StorageBackend:
        return StorageBackend.LocalFile

    async def resolve(self, uri: Uri) -> Storage:
        if uri.protocol == Protocol.File:
            root_path = Path(uri.path)
            return LocalFileStorage(uri, root_path)
        else:
            raise ValueError("Unsupported protocol")
