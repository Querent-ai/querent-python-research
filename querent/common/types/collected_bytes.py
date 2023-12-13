from typing import Union


class CollectedBytes:
    def __init__(self, file: str, data: bytes, error: str = None, eof: bool = False):
        self.data = data
        self.error = error
        self.file = file
        self.eof = eof
        if self.file:
            file = str(file)
            self.extension = file.split(".")[-1]
            self.file_id = file.split("/")[-1].split(".")[0]

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Data: {self.data}"

    def is_error(self) -> bool:
        return self.error is not None

    def is_eof(self) -> bool:
        return self.eof

    def get_file_path(self) -> str:
        return self.file

    def get_extension(self) -> str:
        return self.extension

    def get_file_id(self) -> str:
        return self.file_id

    @classmethod
    def success(cls, data: bytes) -> "CollectedBytes":
        return cls(data)

    @classmethod
    def error(cls, error: str) -> "CollectedBytes":
        return cls(None, error)

    def unwrap(self) -> bytes:
        if self.error:
            raise ValueError(self.error)
        return self.data

    def unwrap_or(self, default: bytes) -> bytes:
        return self.data if not self.error else default

    def __eq__(self, other: Union[bytes, "CollectedBytes"]) -> bool:
        if isinstance(other, CollectedBytes):
            return self.data == other.data and self.error == other.error
        return self.data == other

    def __hash__(self) -> int:
        return hash((self.data, self.error))
