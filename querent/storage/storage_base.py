from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO

class Storage(ABC):
    @abstractmethod
    async def check_connectivity(self) -> None:
        pass

    @abstractmethod
    async def put(self, path: Path, payload) -> None:
        pass

    @abstractmethod
    async def copy_to(self, path: Path, output: IO[bytes]) -> None:
        pass

    async def copy_to_file(self, path: Path, output_path: Path) -> None:
        async with open(output_path, "wb") as output_file:
            await self.copy_to(path, output_file)

    @abstractmethod
    async def get_slice(self, path: Path, start: int, end: int) -> bytes:
        pass

    @abstractmethod
    async def get_all(self, path: Path) -> bytes:
        pass

    @abstractmethod
    async def delete(self, path: Path) -> None:
        pass

    @abstractmethod
    async def bulk_delete(self, paths: list[Path]) -> None:
        pass

    @abstractmethod
    async def exists(self, path: Path) -> bool:
        pass

    @abstractmethod
    async def file_num_bytes(self, path: Path) -> int:
        pass

    @property
    @abstractmethod
    def uri(self) -> str:
        pass
