from typing import Union


class IngestedImages:
    def __init__(
        self,
        file: str,
        image: str,
        image_name: str,
        page_num: int,
        text: [str],
        coordinates: list = [],
        ocr_text: list = [],
        error: str = None,
    ) -> None:
        self.file = file
        self.text = text
        self.error = error
        self.image = image
        self.image_name = image_name
        self.page_num = page_num
        self.coordinates = coordinates
        self.ocr_text = ocr_text
        file = str(file)
        self.extension = file.split(".")[-1]
        self.file_id = file.split("/")[-1].split(".")[0]

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Data: {self.ocr_text}"

    def is_error(self) -> bool:
        return self.error is not None

    def get_extension(self) -> str:
        return self.extension

    def get_file_id(self) -> str:
        return self.file_id
