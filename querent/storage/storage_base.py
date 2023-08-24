from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO
from typing import List

from querent.common.uri import Uri
from querent.storage.payload import PutPayload
from querent.storage.storage_result import StorageResult


class Storage(ABC):
    @abstractmethod
    async def check_connectivity(self) -> None:
        pass

    @abstractmethod
    async def put(self, path: Path, payload: PutPayload) -> StorageResult:
        pass

    @abstractmethod
    async def copy_to(self, path: Path, output: IO[bytes]) -> StorageResult:
        pass

    async def copy_to_file(self, path: Path, output_path: Path) -> StorageResult:
        async with open(output_path, "wb") as output_file:
            await self.copy_to(path, output_file)

    @abstractmethod
    async def get_slice(self, path: Path, start: int, end: int) -> StorageResult:
        pass

    @abstractmethod
    async def get_all(self, path: Path) -> StorageResult:
        pass

    @abstractmethod
    async def delete(self, path: Path) -> StorageResult:
        pass

    @abstractmethod
    async def bulk_delete(self, paths: List[Path]) -> None:
        pass

    @abstractmethod
    async def exists(self, path: Path) -> StorageResult:
        pass

    @abstractmethod
    async def file_num_bytes(self, path: Path) -> StorageResult:
        pass

    @property
    @abstractmethod
    def get_uri(self) -> Uri:
        pass
