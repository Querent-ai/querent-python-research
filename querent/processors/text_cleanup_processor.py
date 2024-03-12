import re

from querent.processors.async_processor import AsyncProcessor
from querent.logging.logger import setup_logger


class TextCleanupProcessor(AsyncProcessor):
    def __init__(self):
        self.logger = setup_logger(__name__, "TextCleanupProcessor")

    async def process_text(self, data: str) -> str:
        data = data.replace("\"", "").replace('\“', '').replace('\”', '')
        data = data.encode('unicode_escape').decode('utf-8')
        data = data.replace("\\n", " ").replace("\\t", " ")
        data = re.sub(r'\\x[0-9a-fA-F]{2}', '', data)

        return data