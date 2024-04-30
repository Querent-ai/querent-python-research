from typing import Any


class EventType:
    Graph = "Graph"
    Vector = "Vector"
    Terminate="Terminate"
    QueryResult="QueryResult"


class EventState:
    def __init__(self, event_type: EventType, timestamp: float, payload: Any, file: str, doc_source: str, image_id: str=None):
        self.event_type = event_type
        self.timestamp = timestamp
        self.payload = payload
        self.file = file
        self.doc_source = doc_source
        self.image_id = image_id
