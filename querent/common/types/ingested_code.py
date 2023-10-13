class IngestedCode:
    """Class for ingested code type of data"""

    def __init__(self, file: str, data: [str], error: str = None) -> None:
        self.data = data
        self.error = error
        self.file = file
        file = str(file)
        self.extension = file.rsplit(".", maxsplit=1)[-1]

    def __str__(self):
        if self.error:
            return f"Error: {self.error}"
        return f"Data: {self.data}"

    def is_error(self) -> bool:
        """Check if there is any error"""
        return self.error is not None

    def get_file_path(self) -> str:
        """Get file path"""
        return self.file

    def get_extension(self) -> str:
        """Get file extension"""
        return self.extension
