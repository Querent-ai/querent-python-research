from typing import Union, List


class IngestedTables:
    def __init__(
        self,
        file: str,
        table: List[List[Union[str, int, float]]],
        page_num: int,
        text: list = [],
        error: str = None,
    ) -> None:
        self.file = file
        self.text = text
        self.error = error
        self.table = table
        self.page_num = page_num
        file = str(file)
        self.extension = file.split(".")[-1]
        self.file_id = file.split("/")[-1].split(".")[0]

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Data: {self.table}"

    def is_error(self) -> bool:
        return self.error is not None

    def get_extension(self) -> str:
        return self.extension

    def get_file_id(self) -> str:
        return self.file_id
