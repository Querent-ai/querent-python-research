"""Querent

Querent is an async data dynamo and inference engine for Python. It is designed to
be used as a library in Python applications that need to perform inference on
data in a scalable and efficient manner. Querent is built on top of the Python
asyncio library and is designed to be used in an async manner.

Querent is the Python Asyncio Inference Engine by Querent AI.
Copyright (c) 2023 by Querent AI.

"""
import asyncio
import signal
from typing import List, Awaitable
from querent.core.base_engine import BaseEngine
from querent.querent.resource_manager import ResourceManager
from querent.querent.auto_scaler import AutoScaler
from querent.logging.logger import setup_logger


class Querent:
    def __init__(
        self,
        querenters: List[BaseEngine],
        resource_manager: ResourceManager,
    ):
        self.logger = setup_logger(__name__, "querent")
        self.resource_manager = resource_manager
        self.querenters = querenters
        self.auto_scaler = AutoScaler(self.resource_manager, querenters)

        # Create an event to handle termination requests
        self.querent_termination_event = resource_manager.querent_termination_event

    async def start(self):
        try:
            self.logger.info("Starting Querent")

            # Start the auto-scaler
            auto_scale_task = asyncio.create_task(self.auto_scaler.start())

            # Start handling signals
            #self.setup_signal_handlers()

            # Start the tasks above and wait for them to finish
            await asyncio.gather(auto_scale_task, self.wait_for_termination())

        except Exception as e:
            self.logger.error(f"An error occurred during Querent execution: {e}")
            await self.graceful_shutdown()
        finally:
            await self.graceful_shutdown()
            self.logger.info("Querent stopped")

    async def graceful_shutdown(self):
        self.logger.info("Initiating graceful shutdown of Querent")

        # Stop the auto-scaler and querenters gracefully
        await self.auto_scaler.stop()

        self.logger.info("Querent stopped gracefully")

    def setup_signal_handlers(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(sig, self.handle_signal)

    def handle_signal(self):
        try:
            shutdown_task = asyncio.create_task(self.graceful_shutdown())
            asyncio.run(shutdown_task)
        except Exception as e:
            print(f"Error during graceful shutdown: {str(e)}")

    async def wait_for_termination(self) -> Awaitable[None]:
        # Wait for the termination event to be set, indicating graceful shutdown
        await self.querent_termination_event.wait()
