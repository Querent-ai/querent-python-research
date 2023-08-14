import asyncio
from pathlib import Path
import tempfile

from querent.collectors.fs.fs_collector import FSCollectorFactory

async def create_test_files(root_dir: Path):
    test_text = "Hello, this is a test file!"
    file_names = ["test_file1.txt", "test_file2.txt"]

    for file_name in file_names:
        file_path = root_dir / file_name
        with open(file_path, "w") as file:
            file.write(test_text)


async def test_fs_collector():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        create_test_files(temp_root)

        collector = FSCollectorFactory().resolve(uri=temp_root)

        async def poll_and_print():
            async for result in collector.poll():
                print(result)

        await collector.connect()
        await poll_and_print()
        await collector.disconnect()


if __name__ == "__main__":
    asyncio.run(test_fs_collector())
