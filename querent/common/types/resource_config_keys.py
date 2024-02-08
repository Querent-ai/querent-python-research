from enum import Enum


class ResourceConfigKey(Enum):
    ID = "id"
    MAX_WORKERS_ALLOWED = "max_workers_allowed"
    MAX_WORKERS_PER_COLLECTOR = "max_workers_per_collector"
    MAX_WORKERS_PER_ENGINE = "max_workers_per_engine"
    MAX_WORKERS_PER_QUERENT = "max_workers_per_querent"
