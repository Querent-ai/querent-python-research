from typing import Iterable
from prometheus_client import Metric


class MetricAdapter:
    def __init__(self):
        raise NotImplementedError

    def update_metric(self, metric_name, value):
        raise NotImplementedError

    def get_metric(self, metric_name) -> Iterable[Metric]:
        raise NotImplementedError
