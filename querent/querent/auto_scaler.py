import asyncio
import logging
from typing import List

from querent.core.base_engine import BaseEngine
from querent.querent.resource_manager import ResourceManager


class AutoScaler:
    def __init__(
        self,
        resource_manager: ResourceManager,
        querenters: List[BaseEngine],
        threshold: int = 10,
    ):
        self.resource_manager = resource_manager
        self.querenters = querenters
        self.threshold = threshold
        self.logger = logging.getLogger("AutoScaler")
        self.querent_termination_event = resource_manager.querent_termination_event
        self.worker_tasks: List[asyncio.Task] = []  # Store the worker tasks

    async def scale_querenters(self, total_requested_workers: int):
        current_total_workers = sum(
            querenter.num_workers for querenter in self.querenters
        )

        if total_requested_workers <= current_total_workers:
            # Scale up querenter workers
            self.worker_tasks = []
            for querenter in self.querenters:
                workers = await querenter.start_workers()
                # Create tasks for the workers and store them
                worker_tasks = [asyncio.create_task(worker) for worker in workers]
                self.worker_tasks.extend(
                    worker_tasks
                )  # Extend the list of worker tasks
                self.logger.info(
                    f"Started {len(worker_tasks)} workers for {querenter.__class__.__name__}"
                )
        else:
            raise Exception("Total requested workers exceed the current total workers.")

    async def start(self):
        try:
            while (
                not self.querent_termination_event.is_set()
            ):  # Check termination_event
                # Calculate the total requested workers for all querenters
                total_requested_workers = sum(
                    querenter.num_workers for querenter in self.querenters
                )
                # Get the maximum allowed workers from the resource manager
                max_allowed_workers = (
                    await self.resource_manager.get_max_allowed_workers()
                )
                if total_requested_workers > max_allowed_workers:
                    raise Exception(
                        "Total requested workers exceed the maximum allowed workers."
                    )

                # Scale querenter workers
                
                await self.scale_querenters(total_requested_workers)

                # Wait for a while before checking again (adjust this as needed)
                await asyncio.sleep(1)

                # Check if all worker tasks have completed
                if all(task.done() for task in self.worker_tasks):
                    self.querent_termination_event.set()  # Set termination event

        except asyncio.CancelledError:
            raise NotImplementedError
        except Exception as e:
            self.logger.error(f"An error occurred during AutoScaler execution: {e}")
            raise e
        finally:
            self.logger.info("AutoScaler stopped")

    async def stop(self):
        self.logger.info("Stopping AutoScaler")
        # Stop the querenter workers
        await self.stop_querenters()
        self.logger.info("AutoScaler stopped")

    async def stop_querenters(self):
        for querenter in self.querenters:
            await querenter.stop_workers()
