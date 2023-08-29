from typing import List
from querent.processors.async_processor import AsyncProcessor


class BaseIngestor:
    def __init__(self, processors: List[AsyncProcessor]):
        self.processors = processors

    async def process_data(self, text):
        # Your common data processing logic here
        pass

    async def extract_text_from_file(self, file_path: str) -> str:
        # Your common file extraction logic here
        pass
