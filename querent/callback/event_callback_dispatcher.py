from collections import defaultdict
from typing import Any, List

import requests
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType


class EventCallbackDispatcher:
    def __init__(self, retries=3):
        self.callbacks: dict[EventType, List[EventCallbackInterface]] = defaultdict(
            list
        )

        self.webhooks: dict[EventType, List[str]] = defaultdict(list)
        self.retries = retries

    def register_callback(
        self, event_type: EventType, callback: EventCallbackInterface
    ):
        """
        Register a callback.
        Args:
            callback (EventCallbackInterface): An event callback instance.
        """
        self.callbacks[event_type].append(callback)

    async def dispatch_event(self, event_type: EventType, event_data: EventState):
        """
        Dispatch an event to all registered callbacks.
        Args:
            event_data (Any): Data associated with the event.
        """
        for callback in self.callbacks[event_type]:
            callback.handle_event(event_type, event_data)

    def register_webhook(self, event_type: EventType, webhook: str):
        """
        Register a webhook.
        Args:
            webhook (str): A webhook.
        """
        self.webhooks[event_type].append(webhook)

    async def dispatch_webhook(self, event_type: EventType, event_data: EventState):
        """
        Dispatch an event to all registered webhooks.
        Args:
            event_data (Any): Data associated with the event.
        """
        for webhook_url in self.webhooks[event_type]:
            # Assuming event_data is a dictionary that you want to send as JSON
            try:
                attempt = 0
                while attempt <= self.retries:
                    response = requests.post(webhook_url, json=event_data)
                    if response.status_code == 200:
                        print(f"Webhook to {webhook_url} was successfully dispatched.")
                        break
                    else:
                        print(
                            f"Failed to dispatch webhook to {webhook_url}. Status code: {response.status_code}"
                        )
                        attempt += 1
            except Exception as e:
                print(f"Error when sending webhook to {webhook_url}: {str(e)}")
