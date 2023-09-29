import asyncio
import logging
import signal
from typing import List, Awaitable
from querent.core.base_engine import BaseEngine
from querent.querent.resource_manager import ResourceManager
from querent.querent.auto_scaler import AutoScaler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Querent")


class Querent:
    def __init__(
        self,
        querenters: List[BaseEngine],
        num_workers: int,
        resource_manager: ResourceManager,
        auto_scale_threshold: int = 10,
    ):
        self.num_workers = num_workers
        self.resource_manager = resource_manager
        self.querenters = querenters
        self.auto_scale_threshold = auto_scale_threshold
        self.auto_scaler = AutoScaler(
            self.resource_manager, querenters, threshold=self.auto_scale_threshold
        )

        # Create an event to handle termination requests
        self.querent_termination_event = resource_manager.querent_termination_event

    async def start(self):
        try:
            logger.info("Starting Querent")

            # Start the auto-scaler
            auto_scale_task = asyncio.create_task(self.auto_scaler.start())

            # Start handling signals
            self.setup_signal_handlers()

            # Start the tasks above and wait for them to finish
            await asyncio.gather(auto_scale_task, self.wait_for_termination())

        except Exception as e:
            logger.error(f"An error occurred during Querent execution: {e}")
            await self.graceful_shutdown()
        finally:
            await self.graceful_shutdown()
            logger.info("Querent stopped")

    async def graceful_shutdown(self):
        logger.info("Initiating graceful shutdown of Querent")

        # Stop the auto-scaler and querenters gracefully
        await self.auto_scaler.stop()

        logger.info("Querent stopped gracefully")

    def setup_signal_handlers(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(sig, self.handle_signal)

    def handle_signal(self):
        try:
            print("Received shutdown signal. Initiating graceful shutdown...")
            shutdown_task = asyncio.create_task(self.graceful_shutdown())
            asyncio.run(shutdown_task)
        except Exception as e:
            print(f"Error during graceful shutdown: {str(e)}")

    async def wait_for_termination(self) -> Awaitable[None]:
        # Wait for the termination event to be set, indicating graceful shutdown
        await self.querent_termination_event.wait()
