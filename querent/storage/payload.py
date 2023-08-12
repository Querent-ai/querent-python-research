from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path

class PutPayload(ABC):
    @abstractmethod
    def len(self) -> int:
        pass

    @abstractmethod
    async def range_byte_stream(self, start: int, end: int) -> bytes:
        pass

    async def byte_stream(self) -> bytes:
        total_len = self.len()
        return await self.range_byte_stream(0, total_len)

    async def read_all(self) -> bytes:
        total_len = self.len()
        return await self.range_byte_stream(0, total_len)
