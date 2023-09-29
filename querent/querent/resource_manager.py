import asyncio
import logging


class ResourceManager:
    def __init__(self, max_allowed_workers=100):
        self.max_allowed_workers = max_allowed_workers
        self.min_allowed_workers = 1
        self.querent_termination_event = asyncio.Event()
        self.logger = logging.getLogger("ResourceManager")

    async def get_max_allowed_workers(self):
        return self.max_allowed_workers

    async def get_min_allowed_workers(self):
        return self.min_allowed_workers

    async def get_desired_workers(self):
        # Your logic to calculate the desired number of workers based on system conditions
        # You can implement your own logic here, e.g., monitoring system load, available resources, etc.
        # For now, returning a constant value for demonstration purposes
        return 10  # Replace with your logic

    async def get_desired_querenters(self):
        # Your logic to calculate the desired number of querenters based on system conditions
        # Similar to get_desired_workers, implement your own logic
        # For now, returning a constant value for demonstration purposes
        return 5  # Replace with your logic

    async def adjust_max_workers(self, new_max_workers):
        # Adjust the maximum allowed workers dynamically based on system conditions
        if new_max_workers < self.min_allowed_workers:
            new_max_workers = self.min_allowed_workers
        elif new_max_workers > self.max_allowed_workers:
            new_max_workers = self.max_allowed_workers

        self.max_allowed_workers = new_max_workers

    async def adjust_min_workers(self, new_min_workers):
        # Adjust the minimum allowed workers dynamically based on system conditions
        if new_min_workers < self.min_allowed_workers:
            new_min_workers = self.min_allowed_workers
        elif new_min_workers > self.max_allowed_workers:
            new_min_workers = self.max_allowed_workers

        self.min_allowed_workers = new_min_workers

    async def is_resource_available(self):
        # Check if there are available resources for more workers
        # Implement your own logic to check resource availability (e.g., CPU, memory)
        # Return True if resources are available, False otherwise
        return True  # Replace with your logic

    async def is_system_overloaded(self):
        # Check if the system is overloaded and should scale down workers
        # Implement your own logic to detect system overload (e.g., high CPU usage)
        # Return True if the system is overloaded, False otherwise
        return False  # Replace with your logic

    async def adjust_resources_based_on_load(self):
        # Check system load and adjust resource allocation accordingly
        if await self.is_system_overloaded():
            # Scale down workers or querenters if the system is overloaded
            await self.adjust_max_workers(self.max_allowed_workers // 2)
            await self.adjust_min_workers(self.min_allowed_workers // 2)
        elif await self.is_resource_available():
            # Scale up workers or querenters if resources are available
            await self.adjust_max_workers(self.max_allowed_workers * 2)
            await self.adjust_min_workers(self.min_allowed_workers * 2)
