import asyncio
import psutil

from querent.logging.logger import setup_logger


class ResourceManager:
    def __init__(self, max_allowed_workers=100):
        self.max_allowed_workers = max_allowed_workers
        self.min_allowed_workers = 1
        self.querent_termination_event = asyncio.Event()
        self.logger = setup_logger(__name__, "resource_manager")

    async def get_max_allowed_workers(self):
        return self.max_allowed_workers

    async def get_min_allowed_workers(self):
        return self.min_allowed_workers

    async def get_desired_workers(self):
        # Your logic to calculate the desired number of workers based on system conditions
        # Monitor CPU usage and memory
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        return int((cpu_percent + memory_percent) / 2)

    async def adjust_max_workers(self, new_max_workers):
        # Adjust the maximum allowed workers dynamically based on system conditions
        if new_max_workers < self.min_allowed_workers:
            new_max_workers = self.min_allowed_workers
        elif new_max_workers > self.max_allowed_workers:
            new_max_workers = self.max_allowed_workers

        self.max_allowed_workers = new_max_workers

    async def is_system_overloaded(self):
        # Check if the system is overloaded based on CPU and memory usage
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent

        # Implement your own logic to detect system overload
        if cpu_percent > 90 or memory_percent > 90:
            return True
        else:
            return False

    async def adjust_resources_based_on_load(self):
        # Check system load and adjust resource allocation accordingly
        if await self.is_system_overloaded():
            # Scale down workers if the system is overloaded
            await self.adjust_max_workers(self.max_allowed_workers // 2)
        else:
            # Scale up workers if the system is not overloaded
            await self.adjust_max_workers(self.max_allowed_workers * 2)
