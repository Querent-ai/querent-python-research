from typing import Optional
from pydantic import BaseModel


class ResourceConfig(BaseModel):
    id: str
    max_workers_allowed: Optional[int]
    max_workers_per_collector: Optional[int]
    max_workers_per_engine: Optional[int]
    max_workers_per_querent: Optional[int]
