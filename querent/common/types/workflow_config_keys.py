from enum import Enum


class WorkflowConfigKey(Enum):
    NAME = "name"
    ID = "id"
    CONFIG = "config"
    INNER_CHANNEL = "inner_channel"
    CHANNEL = "channel"
    INNER_EVENT_HANDLER = "inner_event_handler"
    EVENT_HANDLER = "event_handler"
