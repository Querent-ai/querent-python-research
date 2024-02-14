from abc import ABC, abstractmethod
import asyncio
from querent.callback.event_callback_dispatcher import EventCallbackDispatcher
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.config.engine.engine_config import EngineConfig
from querent.logging.logger import setup_logger
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_images import IngestedImages
import uuid

"""
    BaseEngine is an abstract base class that provides the foundational structure and methods 
    for processing tokens asynchronously and managing event states in a queue-based system.

    Attributes:
        input_queue (QuerentQueue): The queue containing input data to be processed.
        config (EngineConfig): The configuration for the engine.

    Methods:
        process_tokens(data: IngestedTokens) -> EventState:
            Abstract method to process tokens asynchronously.

        process_messages(data: IngestedMessages) -> EventState:
            Abstract method to process chat asynchronously.

        validate() -> bool:
            Abstract method to validate the configuration of the engine.

        set_state(new_state: EventState) -> None:
            Set the state to a new value.

        _listen_for_state_changes() -> None:
            Listen for changes in the state and notify subscribers.

        _worker() -> None:
            Worker task to process tokens and manage retries.

        _start_workers(number_of_workers: int) -> list:
            Start the specified number of worker tasks.

        _stop_workers() -> None:
            Stop all worker tasks.

        subscribe(event_type: EventType, callback: Callable) -> None:
            Subscribe to a specific event type.

        _notify_subscribers(event_type: EventType, event_state: EventState) -> None:
            Notify subscribers when an event occurs.

        set_termination_event() -> None:
            Set the termination event to signal termination of workers and listeners.
    """


class BaseEngine(ABC):
    def __init__(
        self,
        input_queue: QuerentQueue,
        config: EngineConfig = EngineConfig(
            config_source={
                "id": str(uuid.uuid4()),
                "name": "BaseEngine",
                "description": "Base Engine",
                "version": "0.0.1",
            }
        ),
        **kwargs,
    ):
        super().__init__(**kwargs)  # Call the super constructor first
        self.input_queue = input_queue
        self.termination_event = asyncio.Event()
        self.state_queue = QuerentQueue()
        self.num_workers = config.num_workers
        self.max_retries = config.max_retries
        self.retry_interval = config.retry_interval
        self.message_throttle_limit = config.message_throttle_limit
        self.message_throttle_delay = config.message_throttle_delay
        self.logger = setup_logger(config.logger, f"{__name__}.base_engine")
        self.callback_dispatcher = EventCallbackDispatcher()

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
    async def process_code(self, data: IngestedCode):
        """
        Process coding files asynchronously.
        Args:
            data (IngestedCode): The input data to process.
        Returns:
            EventState: The state of the event is set with the event type and the timestamp
            of the event and set using `self.set_state(event_state)`.
        """
        raise NotImplementedError

    @abstractmethod
    async def process_images(self, data: IngestedImages):
        """
        Process image files asynchronously.
        Args:
            data (IngestedImage): The input data to process.
        Returns:
            EventState: The state of the event is set with the event type and the timestamp
            of the event and set using `self.set_state(event_state)`.
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate the LLM.
        Returns:
            bool: True if the LLM is valid, False otherwise.
        """
        raise NotImplementedError

    def set_termination_event(self):
        """
        Set termination event: Extensions of base engines must call this method to signal termination of workers and listeners.
        """
        self.termination_event.set()

    def subscribe(self, event_type: EventType, callback: EventCallbackInterface):
        """
        Subscribe to a specific event type.
        Args:
            event_type (EventType): The type of event to subscribe to (e.g., "token_processed").
            callback (Callable): The callback function to be invoked when the event occurs.
        """
        self.callback_dispatcher.register_callback(event_type, callback)

    async def set_state(self, new_state: EventState):
        """
        Set the state to a new value.
        Args:
            new_state (EventState): The new state.
        """
        if isinstance(new_state, EventState):
            await self.state_queue.put(new_state)
        else:
            raise Exception(
                f"Bad state type {type(new_state)} for {self.__class__.__name__}. Supported type: {EventState}"
            )

    """
        The following methods enables independent processing of tokens and messages.
    """

    async def _listen_for_state_changes(self):
        while not self.state_queue.empty() or not self.termination_event.is_set():
            new_state = await self.state_queue.get()
            if isinstance(new_state, EventState):
                if new_state.payload == "Terminate":
                    break
                new_state = {
                    "event_type": new_state.event_type,
                    "timestamp": new_state.timestamp,
                    "payload": new_state.payload,
                    "file": new_state.file
                }
                await self._notify_subscribers(new_state["event_type"], new_state)
            else:
                raise Exception(
                    f"Bad state type {type(new_state)} for {self.__class__.__name__}. Supported type: {EventState}"
                )
            await self.state_queue.task_done()

    async def _notify_subscribers(self, event_type: EventType, event_state: EventState):
        """
        Notify subscribers when an event occurs.
        Args:
            event_type (EventType): The type of event that occurred.
            event_data (EventState): The data associated with the event.
        """
        await self.callback_dispatcher.dispatch_event(event_type, event_state)
        await self.callback_dispatcher.dispatch_webhook(event_type, event_state)

    async def _worker(self):
        try:
            if not self.validate():
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Please check the configuration."
                )
                raise ValueError(
                    f"Invalid {self.__class__.__name__} configuration. Please check the configuration."
                )

            state_listener = asyncio.create_task(self._listen_for_state_changes())

            async def _inner_worker():
                current_message_total = 0
                while not self.termination_event.is_set():
                    retries = 0
                    none_counter = 0
                    try:
                        data = await asyncio.wait_for(self.input_queue.get(), timeout=240)
                        try:
                            if isinstance(data, IngestedMessages):
                                await self.process_messages(data)
                            elif isinstance(data, IngestedTokens):
                                await self.process_tokens(data)
                            elif isinstance(data, IngestedImages):
                                await self.process_images(data)
                            elif isinstance(data, IngestedCode):
                                await self.process_code(data)
                            elif data is None:
                                none_counter += 1
                                if none_counter >= 2:
                                    self.termination_event.set()
                                    current_state = EventState(EventType.Terminate,1.0, "Terminate", "temp.txt")
                                    await self.set_state(new_state=current_state)

                            else:
                                raise Exception(
                                    f"Invalid data type {type(data)} for {self.__class__.__name__}. Supported type: {IngestedTokens, IngestedMessages}"
                                )
                        except Exception as e:
                            self.logger.error(
                                f"Error processing tokens: {e}. Retrying ({retries}/{self.max_retries})"
                            )
                            retries += 1

                            if retries > self.max_retries:
                                self.logger.error(
                                    f"Error processing tokens: {e}. Max retries reached. Terminating."
                                )
                                break
                        
                        await asyncio.sleep(self.retry_interval)

                    except asyncio.TimeoutError:
                        self.termination_event.set()
                        current_state = EventState(EventType.Terminate,1.0, "Terminate", "temp.txt")
                        await self.set_state(new_state=current_state)

                    current_message_total += 1

                    if current_message_total >= self.message_throttle_limit:
                        await asyncio.sleep(self.message_throttle_delay)
                        current_message_total = 0

            await asyncio.gather(state_listener, _inner_worker())
        except Exception as e:
            self.logger.error(f"Error while processing tokens: {e}")
        finally:
            self.logger.info(f"Stopping worker for {self.__class__.__name__}")
            self.logger.info(f"Stopped worker for {self.__class__.__name__}")
            self.termination_event.set()

    async def _start_workers(self):
        self.workers = [self._worker() for _ in range(self.num_workers)]
        return self.workers

    async def _stop_workers(self):
        try:
            self.termination_event.set()
        except Exception as e:
            self.logger.error(f"Error while stopping workers: {e}")
