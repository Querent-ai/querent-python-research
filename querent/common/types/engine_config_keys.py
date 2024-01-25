from enum import Enum


class EngineConfigKey(Enum):
    ID = "id"
    NAME = "name"
    NUM_WORKERS = "num_workers"
    MAX_RETRIES = "max_retries"
    RETRY_INTERVAL = "retry_interval"
    MESSAGE_THROTTLE_LIMIT = "message_throttle_limit"
    MESSAGE_THROTTLE_DELAY = "message_throttle_delay"
    INNER_CHANNEL = "inner_channel"
    CHANNEL = "channel"
