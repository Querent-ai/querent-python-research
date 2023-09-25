import asyncio
import signal


class SignalHandler:
    def __init__(self, querent):
        self.querent = querent

    async def handle_signals(self):
        for sig in [signal.SIGINT, signal.SIGTERM]:
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(sig, self.handle_signal)

    async def handle_signal(self):
        try:
            print("Received shutdown signal. Initiating graceful shutdown...")
            await self.querent.graceful_shutdown()
        except Exception as e:
            print(f"Error during graceful shutdown: {str(e)}")
        finally:
            print("Querent stopped")
            exit(0)
