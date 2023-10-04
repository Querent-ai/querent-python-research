from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
"""
    BaseEngine is an abstract base class that provides the foundational structure and methods 
    for processing tokens asynchronously and managing event states in a queue-based system.

    Attributes:
        input_queue (QuerentQueue): The queue containing input data to be processed.
        num_workers (int): Number of worker tasks to spawn for processing.
        max_retries (int): Maximum number of retries for processing tokens in case of failure.
        retry_interval (float): Time interval (in seconds) between retries.
        message_throttle_limit (int): Limit for message processing to prevent overwhelming subscribers.
        message_throttle_delay (float): Delay (in seconds) between processing messages to throttle the rate.
        termination_event (asyncio.Event): Event to signal termination of workers and listeners.
        logger (logging.Logger): Logger instance for logging messages and errors.
        workers (list): List of worker tasks.
        subscribers (dict): Mapping of event types to their respective subscriber callback functions.
        state_queue (asyncio.Queue): Queue to store and manage event states.

    Methods:
        process_tokens(data: IngestedTokens) -> EventState:
            Abstract method to process tokens asynchronously.

        validate() -> bool:
            Abstract method to validate the configuration of the engine.

        set_state(new_state: EventState) -> None:
            Set the state to a new value.

        listen_for_state_changes() -> None:
            Listen for changes in the state and notify subscribers.

        worker() -> None:
            Worker task to process tokens and manage retries.

        start_workers(number_of_workers: int) -> list:
            Start the specified number of worker tasks.

        stop_workers() -> None:
            Stop all worker tasks.

        subscribe(event_type: EventType, callback: Callable) -> None:
            Subscribe to a specific event type.

        _notify_subscribers(event_type: EventType, event_state: EventState) -> None:
            Notify subscribers when an event occurs.

        set_termination_event() -> None:
            Set the termination event to signal termination of workers and listeners.
    """


class BaseEngine(ABC):
    subscribers: Dict[EventType, List[Callable]] = {}
    termination_event: asyncio.Event = asyncio.Event()
    state_queue: QuerentQueue = QuerentQueue()
    workers: List[Any] = []
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self,
        input_queue: QuerentQueue,
        num_workers: int = 1,
        max_retries: int = 3,
        retry_interval: float = 2.0,
        message_throttle_limit: int = 100,
        message_throttle_delay: float = 0.1,
        **kwargs,
    ):
        super().__init__(**kwargs)  # Call the super constructor first
        self.input_queue = input_queue
        self.num_workers = num_workers
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.message_throttle_limit = message_throttle_limit
        self.message_throttle_delay = message_throttle_delay

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
    async def process_messages(self, data: IngestedMessages):
        """
        Process chat asynchronously.
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

    @classmethod
    async def set_state(cls, new_state: EventState):
        """
        Set the state to a new value.
        Args:
            new_state (EventState): The new state.
        """
        if isinstance(new_state, EventState):
            await cls.state_queue.put(new_state)
        else:
            cls.termination_event.set()
            raise Exception(
                f"Bad state type {type(new_state)} for {cls.__class__.__name__}. Supported type: {EventState}"
            )

    @classmethod
    def subscribe(cls, event_type: EventType, callback: Callable):
        """
        Subscribe to a specific event type.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            callback (Callable): The callback function to be invoked when the event occurs.
        """
        if event_type not in cls.subscribers:
            cls.subscribers[event_type] = []
        cls.subscribers[event_type].append(callback)

    @classmethod
    def set_termination_event(cls):
        """
        Set termination event
        """
        cls.termination_event.set()

    @classmethod
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
            self.state_queue.task_done()

    @classmethod
    async def worker(cls):
        try:
            if not cls.validate():
                raise Exception(
                    f"Invalid {cls.__class__.__name__} configuration. Please check the configuration."
                )
            state_listener = asyncio.create_task(cls.listen_for_state_changes())
            while not cls.termination_event.is_set():
                data = await cls.input_queue.get()
                retries = 0
                while retries <= cls.max_retries:
                    try:
                        if isinstance(data, IngestedMessages):
                            await cls.process_messages(data)
                        elif isinstance(data, IngestedTokens):
                            await cls.process_tokens(data)
                        else:
                            raise Exception(
                                f"Invalid data type {type(data)} for {cls.__class__.__name__}. Supported type: {IngestedTokens, IngestedMessages}"
                            )
                    except Exception as e:
                        cls.logger.error(
                            f"Error processing tokens: {e}. Retrying ({retries}/{cls.max_retries})"
                        )
                        retries += 1
                        if retries <= cls.max_retries:
                            await asyncio.sleep(cls.retry_interval)
                        else:
                            raise e
                # Throttle message processing to prevent overwhelming subscribers
                await asyncio.sleep(cls.message_throttle_delay)

                await cls.input_queue.task_done()

            await state_listener  # Wait for the state listener to finish
        except Exception as e:
            cls.termination_event.set()
            cls.logger.error(f"Error while processing tokens: {e}")

    @classmethod
    async def start_workers(cls):
        cls.workers = [cls.worker() for _ in range(cls.num_workers)]
        return cls.workers

    @classmethod
    async def stop_workers(cls):
        try:
            cls.termination_event.set()
            await asyncio.gather(*cls.workers)
        except Exception as e:
            cls.logger.error(f"Error while stopping workers: {e}")

    @classmethod
    async def _notify_subscribers(cls, event_type: EventType, event_state: EventState):
        """
        Notify subscribers when an event occurs.
        Args:
            event_type (EventType): The type of event that occurred.
            event_data (EventState): The data associated with the event.
        """
        if event_type in cls.subscribers:
            for callback in cls.subscribers[event_type]:
                await asyncio.gather(callback(event_state))

