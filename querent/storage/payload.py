import io
from abc import ABC, abstractmethod
from typing import Optional


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

    async def read(self, n: Optional[int] = None) -> bytes:
        if n is None:
            return await self.byte_stream()
        return await self.range_byte_stream(0, n)
    
    async def read_all(self) -> bytes:
        total_len = self.len()
        return await self.range_byte_stream(0, total_len)

class BytesPayload(PutPayload):
    def __init__(self, data: bytes):
        self.data = data

    def len(self) -> int:
        return len(self.data)

    async def range_byte_stream(self, start: int, end: int) -> bytes:
        start = max(start, 0)
        end = min(end, len(self.data))
        return self.data[start:end]

    async def read(self, n: Optional[int] = None) -> bytes:
        if n is None:
            return await self.byte_stream()
        return await self.range_byte_stream(0, n)

    async def read_all(self) -> bytes:
        return await self.byte_stream()

class ByteStream:
    def __init__(self, data: bytes):
        self.data = data

    async def read(self, n: Optional[int] = None) -> bytes:
        if n is None:
            return self.data
        return self.data[:n]


# Example usage
async def main():
    payload_data = b"test content"
    payload = BytesPayload(payload_data)
    
    byte_stream = ByteStream(payload_data)
    result = await byte_stream.read(4)
    print(result)  # Output: b"test"


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
