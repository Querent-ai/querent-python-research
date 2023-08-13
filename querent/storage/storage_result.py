from typing import Any, Union

class StorageResult:
    def __init__(self, value: Any, error: str = None) -> None:
        self.value = value
        self.error = error

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Value: {self.value}"

    def is_error(self) -> bool:
        return self.error is not None

    @classmethod
    def success(cls, value: Any) -> "StorageResult":
        return cls(value)

    @classmethod
    def error(cls, error: str) -> "StorageResult":
        return cls(None, error)

    def unwrap(self) -> Any:
        if self.error:
            raise ValueError(self.error)
        return self.value

    def unwrap_or(self, default: Any) -> Any:
        return self.value if not self.error else default

    def __eq__(self, other: Union[Any, "StorageResult"]) -> bool:
        if isinstance(other, StorageResult):
            return self.value == other.value and self.error == other.error
        return self.value == other

    def __hash__(self) -> int:
        return hash((self.value, self.error))


# Usage example
if __name__ == "__main__":
    success_result = StorageResult.success("Success value")
    print(success_result)

    error_result = StorageResult.error("An error occurred")
    print(error_result)

    unwrapped_value = success_result.unwrap()
    print("Unwrapped:", unwrapped_value)

    default_value = success_result.unwrap_or("Default value")
    print("Unwrapped with default:", default_value)

    print("Equality:", success_result == "Success value")
    print("Equality:", success_result == StorageResult.success("Success value"))
