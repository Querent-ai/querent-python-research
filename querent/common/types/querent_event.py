from typing import Any


class EventType:
    Graph = "Graph"
    Vector = "Vector"
    Terminate="Terminate"


class EventState:
    def __init__(self, event_type: EventType, timestamp: float, payload: Any, file: str):
        self.event_type = event_type
        self.timestamp = timestamp
        self.payload = payload
        self.file = file
        self.file = file
