from enum import Enum


class IngestorError(Enum):
    EOF = "End of File"
    ETCD = "ETCD Error"
    NETWORK = "Network Error"
    TIMEOUT = "Timeout"
    UNKNOWN = "Unknown Error"
