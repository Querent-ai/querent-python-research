from typing import Any, Tuple, List
from pathlib import Path
from functools import lru_cache
import asyncio
from querent.storage.base import Storage, StorageResult, PutPayload, SendableAsync
from querent.common.uri import Uri
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Optional, Dict, Callable
from fnv import hash
from asyncio.futures import Future
from asyncio import Lock
import tempfile

class AsyncDebouncer(K, V: Clone):
    def __init__(self):
        self.cache = {}

    def len(self):
        return len(self.cache)

    def cleanup(self):
        self.cache = {k: v for k, v in self.cache.items() if v.future.done()}

    async def get_or_create(self, key: K, build_a_future: Callable[[], V]) -> V:
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
    def __init__(self, future: Future):
        self.future = future

class DebouncedStorage(Storage):
    def __init__(self, underlying: Storage):
        self.underlying = underlying
        self.slice_debouncer = AsyncDebouncer[DebouncerKey, StorageResult[bytes]]()

    async def check_connectivity(self) -> Any:
        return await self.underlying.check_connectivity()

    async def put(self, path: Path, payload: PutPayload) -> None:
        await self.underlying.put(path, payload)

    async def copy_to(self, path: Path, output: SendableAsync) -> None:
        await self.underlying.copy_to(path, output)

    async def get_slice(self, path: Path, range_: Tuple[int, int]) -> StorageResult:
        key = (path, range_)
        cached_result = await self.get_slice_cache(key)
        if cached_result is None:
            result = await self.underlying.get_slice(path, range_)
            await self.set_slice_cache(key, result)
            return result
        return cached_result

    @lru_cache(maxsize=128)  # Using functools.lru_cache for caching
    def get_slice_cache(self, key: Tuple[Path, Tuple[int, int]]) -> Any:
        pass

    async def set_slice_cache(self, key: Tuple[Path, Tuple[int, int]], value: Any) -> None:
        pass

    async def delete(self, path: Path) -> None:
        await self.underlying.delete(path)

    async def bulk_delete(self, paths: List[Path]) -> None:
        await self.underlying.bulk_delete(paths)

    async def get_all(self, path: Path) -> Any:
        key = (path, 0, float('inf'))
        cached_result = await self.get_slice_cache(key)
        if cached_result is None:
            result = await self.underlying.get_all(path)
            await self.set_slice_cache(key, result)
            return result
        return cached_result

    async def file_num_bytes(self, path: Path) -> int:
        return await self.underlying.file_num_bytes(path)

    def uri(self) -> str:
        return self.underlying.uri()

class LocalFileStorage(Storage):
    def __init__(self, uri: Uri, root: Path):
        self.uri = uri
        self.root = root
        self.cache_lock = Lock()

    async def full_path(self, relative_path: Path) -> Path:
        await self.ensure_valid_relative_path(relative_path)
        return self.root / relative_path

    async def ensure_valid_relative_path(self, path: Path) -> None:
        async with self.cache_lock:
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
        full_path = await self.full_path(path)
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
        full_path = await self.full_path(relative_path)
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

    async def bulk_delete(self, paths: List[Path]) -> None:
        async with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_path = {
                executor.submit(self.delete_single_file, path): path for path in paths
            }
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

    async def get_all(self, path: Path) -> bytes:
        full_path = await self.full_path(path)
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
