import asyncio
import fnmatch
import re
from pathlib import Path
from typing import AsyncGenerator
from querent.collectors.collector_base import Collector
from querent.collectors.collector_factory import CollectorFactory
from querent.common.types.collected_bytes import CollectedBytes
from querent.common.uri import Uri
from querent.config.collector_config import CollectorBackend, FSCollectorConfig
import aiofiles
from querent.common import common_errors


class FSCollector(Collector):
    def __init__(self, config: FSCollectorConfig):
        self.root_dir = Path(config.root_path)
        self.items_to_ignore = []
        self.chunk_size = config.chunk_size

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    # collect those files

    async def poll(self) -> AsyncGenerator[CollectedBytes, None]:
        async for file_path in self.walk_files(self.root_dir):
            try:
                async with aiofiles.open(file_path, "rb") as file:
                    async for chunk in self.read_chunks(file):
                        yield CollectedBytes(file=file_path, data=chunk, error=None)
            except PermissionError as exc:
                raise common_errors.PermissionError(
                    f"Unable to open this file {file_path}, getting error as {exc}"
                ) from exc
            except OSError as exc:
                raise common_errors.OSError(
                    f"Getting OS Error on file {file_path}, as {exc}"
                ) from exc

    async def read_chunks(self, file):
        while True:
            chunk = await file.read(self.chunk_size)
            if not chunk:
                break
            yield chunk
        await file.close()

    async def walk_files(self, root: Path) -> AsyncGenerator[Path, None]:
        with open("./.gitignore", "r", encoding="utf-8") as gitignore_file:
            self.items_to_ignore = gitignore_file.read().splitlines()

        gitignore_regex = self.build_gitignore_regex(self.items_to_ignore)
        for item in root.iterdir():
            # print("item   ", item, "    ", type(item))
            # try:
            #     print(
            #         "gitignore_regex.search(item)    ",
            #         bool(gitignore_regex.search(str(item))),
            #     )
            # except Exception as e:
            #     print(e)
            if bool(gitignore_regex.search(str(item))):
                continue
            if item.is_file():
                yield item
            elif item.is_dir():
                async for file_path in self.walk_files(item):
                    yield file_path

    def build_gitignore_regex(self, gitignore_patterns):
        gitignore_patterns = [
            pattern for pattern in gitignore_patterns if pattern != "*.py"
        ]
        combined_pattern = "|".join(
            fnmatch.translate(pattern) for pattern in gitignore_patterns
        )
        return re.compile(f"({combined_pattern})")


class FSCollectorFactory(CollectorFactory):
    def __init__(self):
        pass

    def backend(self) -> CollectorBackend:
        return CollectorBackend.LocalFile

    def resolve(self, uri: Uri, config: FSCollectorConfig) -> Collector:
        return FSCollector(config)
