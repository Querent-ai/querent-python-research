from typing import Union


class IngestedTokens:
    def __init__(
        self, file: str, data: [str], error: str = None, is_token_stream=False
    ) -> None:
        self.data = data
        self.error = error
        self.is_token_stream = is_token_stream
        if file:
            self.file = file
            file = str(file)
            self.extension = file.split(".")[-1]
            self.file_id = file.split("/")[-1].split(".")[0]

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Data: {self.data}"

    def is_error(self) -> bool:
        return self.error is not None

    def get_file_path(self) -> str:
        return self.file

    def get_extension(self) -> str:
        return self.extension

    def get_file_id(self) -> str:
        return self.file_id

    @classmethod
    def success(cls, data: bytes) -> "IngestedTokens":
        return cls(data)

    @classmethod
    def error(cls, error: str) -> "IngestedTokens":
        return cls(None, error)

    def unwrap(self) -> bytes:
        if self.error:
            raise ValueError(self.error)
        return self.data

    def unwrap_or(self, default: bytes) -> bytes:
        return self.data if not self.error else default

    def __eq__(self, other: Union[bytes, "IngestedTokens"]) -> bool:
        if isinstance(other, IngestedTokens):
            return self.data == other.data and self.error == other.error
        return self.data == other

    def __hash__(self) -> int:
        return hash((self.data, self.error))
