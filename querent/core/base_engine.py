from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class BaseEngine(ABC):
    def __init__(
        self,
        input_queue: QuerentQueue,
        num_workers: int = 1,
        max_retries: int = 3,
        retry_interval: float = 2.0,
        message_throttle_limit: int = 100,
        message_throttle_delay: float = 0.1,
        max_state_transitions: int = 1000,
    ):
        self.input_queue = input_queue
        self.num_workers = num_workers
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.message_throttle_limit = message_throttle_limit
        self.message_throttle_delay = message_throttle_delay
        self.max_state_transitions = max_state_transitions
        self.termination_event = asyncio.Event()
        self.logger = logging.getLogger(self.__class__.__name__)  # Initialize logger
        self.workers = []
        self.subscribers: Dict[
            EventType, List[Callable]
        ] = {}  # Event-type to subscribers mapping
        self.state_queue: asyncio.Queue = asyncio.Queue(
            maxsize=max_state_transitions  # these many at a given time
        )  # Limited queue size

    @abstractmethod
    async def process_tokens(self, data: IngestedTokens):
        """
        Process tokens asynchronously.
        Args:
            data (IngestedTokens): The input data to process.
        Returns:
            EventState: The state of the event is set with the event type and the timestamp
            of the event and set using `self.set_state(event_state)`.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the LLM.
        Returns:
            bool: True if the LLM is valid, False otherwise.
        """
        raise NotImplementedError

    async def set_state(self, new_state: EventState):
        """
        Set the state to a new value.
        Args:
            new_state (EventState): The new state.
        """
        if isinstance(new_state, EventState):
            await self.state_queue.put(new_state)
        else:
            self.termination_event.set()
            raise Exception(
                f"Bad state type {type(new_state)} for {self.__class__.__name__}. Supported type: {EventState}"
            )

    async def listen_for_state_changes(self):
        while not self.termination_event.is_set():
            new_state = await self.state_queue.get()
            if isinstance(new_state, EventState):
                await self._notify_subscribers(new_state.event_type, new_state)
            else:
                self.termination_event.set()
                raise Exception(
                    f"Bad state type {type(new_state)} for {self.__class__.__name__}. Supported type: {EventState}"
                )

    async def worker(self):
        try:
            if not self.validate():
                raise Exception(
                    f"Invalid {self.__class__.__name__} configuration. Please check the configuration."
                )
            state_listener = asyncio.create_task(self.listen_for_state_changes())
            while not self.termination_event.is_set():
                data = await self.input_queue.get()
                if isinstance(data, IngestedTokens):
                    retries = 0
                    while retries <= self.max_retries:
                        try:
                            await self.process_tokens(data)
                            break  # Successful processing, exit retry loop
                        except Exception as e:
                            self.logger.error(
                                f"Error processing tokens: {e}. Retrying ({retries}/{self.max_retries})"
                            )
                            retries += 1
                            if retries <= self.max_retries:
                                await asyncio.sleep(self.retry_interval)
                            else:
                                raise e
                else:
                    raise Exception(
                        f"Invalid data type {type(data)} for {self.__class__.__name__}. Supported type: {IngestedTokens}"
                    )

                # Throttle message processing to prevent overwhelming subscribers
                await asyncio.sleep(self.message_throttle_delay)

                self.input_queue.task_done()

            await state_listener  # Wait for the state listener to finish
        except Exception as e:
            self.termination_event.set()
            self.logger.error(f"Worker error: {e}")

    async def start_workers(self):
        self.workers = [self.worker() for _ in range(self.num_workers)]
        return self.workers

    async def stop_workers(self):
        try:
            self.termination_event.set()
            await asyncio.gather(*self.workers)
        except Exception as e:
            self.logger.error(f"Error while stopping workers: {e}")

    def subscribe(self, event_type: EventType, callback: Callable):
        """
        Subscribe to a specific event type.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            callback (Callable): The callback function to be invoked when the event occurs.
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    async def _notify_subscribers(self, event_type: EventType, event_state: EventState):
        """
        Notify subscribers when an event occurs.
        Args:
            event_type (EventType): The type of event that occurred.
            event_data (EventState): The data associated with the event.
        """
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                await asyncio.gather(callback(event_state))
