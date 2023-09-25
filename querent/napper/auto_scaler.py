import logging
from typing import List

from querent.llm.base_llm import BaseLLM
from querent.napper.resource_manager import ResourceManager


class AutoScaler:
    def __init__(
        self, resource_manager: ResourceManager, querenters: List[BaseLLM], threshold=10
    ):
        self.resource_manager = resource_manager
        self.querenters = querenters
        self.threshold = threshold
        self.logger = logging.getLogger("AutoScaler")

    async def scale_querenters(self, total_requested_workers):
        current_total_workers = sum(
            querenter.num_workers for querenter in self.querenters
        )

        if total_requested_workers >= current_total_workers:
            # Scale up querenter workers
            for querenter in self.querenters:
                num_workers_to_scale = querenter.num_workers
                await querenter.start_workers(num_workers_to_scale)

        elif total_requested_workers < current_total_workers:
            # Scale down querenter workers
            for querenter in self.querenters:
                num_workers_to_scale = querenter.num_workers
                await querenter.stop_workers(num_workers_to_scale)

        self.logger.info(
            f"Scaled querenter workers to {total_requested_workers} workers in total"
        )

    async def start(self):
        try:
            # Calculate the total requested workers for all querenters
            total_requested_workers = sum(
                querenter.num_workers for querenter in self.querenters
            )

            # Get the maximum allowed workers from the resource manager
            max_allowed_workers = await self.resource_manager.get_max_allowed_workers()

            if total_requested_workers > max_allowed_workers:
                raise Exception(
                    "Total requested workers exceed the maximum allowed workers."
                )

            # Scale the number of querenter workers
            await self.scale_querenters(total_requested_workers)

        except Exception as e:
            self.logger.error(f"An error occurred during AutoScaler execution: {e}")

    async def stop(self):
        self.logger.info("Stopping AutoScaler")
        # Stop the querenter workers
        await self.stop_querenters()
        self.logger.info("AutoScaler stopped")

    async def stop_querenters(self):
        for querenter in self.querenters:
            await querenter.stop_workers()
