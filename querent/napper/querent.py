import asyncio
import logging
import signal
from typing import List
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_llm import BaseLLM
from querent.napper.resource_manager import ResourceManager
from querent.napper.auto_scaler import AutoScaler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Querent")


class Querent:
    def __init__(
        self,
        querenters: List[BaseLLM],
        num_workers: int,
        max_workers: int,
        resource_manager: ResourceManager,
        auto_scale_threshold: int = 10,
    ):
        self.num_workers = num_workers
        self.max_workers = max_workers
        self.resource_manager = resource_manager
        self.querenters = querenters
        self.auto_scale_threshold = auto_scale_threshold
        self.auto_scaler = AutoScaler(
            self.resource_manager, querenters, threshold=self.auto_scale_threshold
        )

    async def start(self):
        try:
            logger.info("Starting Querent")

            # Start the auto-scaler
            asyncio.create_task(self.auto_scaler.run())

        except Exception as e:
            logger.error(f"An error occurred during Querent execution: {e}")
            await self.graceful_shutdown()
        finally:
            # Stop the workers
            await asyncio.gather(
                *(querenter.stop_workers() for querenter in self.querenters)
            )
            logger.info("Querent stopped")

    async def graceful_shutdown(self):
        logger.info("Initiating graceful shutdown of Querent")

        # Stop the auto-scaler and querenters gracefully
        await self.auto_scaler.stop()

        # Stop the workers
        await asyncio.gather(
            *(querenter.stop_workers() for querenter in self.querenters)
        )

        logger.info("Querent stopped gracefully")

    async def handle_shutdown(self):
        try:
            # Wait for a KeyboardInterrupt (Ctrl+C) or SIGTERM to initiate graceful shutdown
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Received shutdown signal (Ctrl+C or SIGTERM)")
            await self.graceful_shutdown()
