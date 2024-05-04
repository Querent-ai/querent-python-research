import re

from querent.processors.async_processor import AsyncProcessor
from querent.logging.logger import setup_logger


class TextCleanupProcessor(AsyncProcessor):
    def __init__(self):
        self.logger = setup_logger(__name__, "TextCleanupProcessor")

    async def process_text(self, data: str) -> str:
        data = data.replace("\"", "").replace('\“', '').replace('\”', '')
        data = data.replace("\\n", " ").replace("\\t", " ")
        data = re.sub(r'\\x[0-9a-fA-F]{2}', '', data)
        data = data.replace("\n", " ").replace("\r", " ").replace("\t", " ")
        data = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]+', '', data)

        return data