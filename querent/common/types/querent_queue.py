import asyncio


class QuerentQueue:
    """
    An asyncio-based queue with some additional functionality.

    This queue allows you to put and get items asynchronously. It also supports marking items as done,
    joining the queue, and closing it with a sentinel value to signal worker exit.

    Example:
        queue = QuerentQueue()
        await queue.put(item)
        item = await queue.get()
        await queue.task_done()
        await queue.close()

    Args:
        None

    Attributes:
        queue (asyncio.Queue): The underlying asyncio queue.

    """

    def __init__(self):
        """
        Initialize a QuerentQueue.
        """
        self.queue = asyncio.Queue()

    async def put(self, item):
        """
        Put an item into the queue asynchronously.

        Args:
            item: The item to put into the queue.

        Returns:
            None

        """
        await self.queue.put(item)

    async def put_nowait(self, item):
        """
        Put an item into the queue asynchronously without waiting.

        Args:
            item: The item to put into the queue.

        Returns:
            None

        """
        self.queue.put_nowait(item)

    async def get(self):
        """
        Get an item from the queue asynchronously.

        Returns:
            Any: The item retrieved from the queue.

        """
        return await self.queue.get()

    async def get_nowait(self):
        """
        Get an item from the queue asynchronously without waiting.

        Returns:
            Any: The item retrieved from the queue.

        """
        return self.queue.get_nowait()

    async def join(self):
        """
        Block until all items in the queue have been processed.

        Returns:
            None

        """
        await self.queue.join()

    async def task_done(self):
        """
        Mark an item as done. This should be called after processing an item retrieved from the queue.

        Returns:
            None

        """
        self.queue.task_done()

    async def close(self):
        """
        Close the queue by putting a sentinel value into it. This signals worker exit.

        Returns:
            None

        """
        await self.queue.put(None)  # Sentinel value to signal worker exit

    def empty(self):
        """
        Check if the queue is empty.

        Returns:
            bool: True if the queue is empty, False otherwise.

        """
        return self.queue.empty()

    def __aiter__(self):
        return self

    async def __anext__(self):
        item = await self.get()
        if item is None:
            raise StopAsyncIteration
        return item
