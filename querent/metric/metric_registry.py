from typing import Iterable

from prometheus_client import Metric
from querent.common.errors.metric_errors import UnknownMetricError, UpdateMetricError
from querent.metric.base_metric_adapter import MetricAdapter


class MetricRegistry:
    def __init__(self):
        self.metric_adapters: dict[str, MetricAdapter] = {}

    def register_metric_adapter(self, metric_name: str, metric_adapter: MetricAdapter):
        """
        Register a metric adapter.
        :param metric_adapter: Metric adapter instance.
        """
        self.metric_adapters[metric_name.lower()] = metric_adapter

    def list_metric_adapters(self):
        """
        List all registered metric adapters.
        :return: List of metric adapter names.
        """
        return list(self.metric_adapters.keys())

    def update_metric(self, metric_name: str, value: int):
        """
        Update the value of a metric.
        :param metric_name: Name of the metric.
        :param value: New value for the metric.
        """
        try:
            self.metric_adapters[metric_name.lower()].update_metric(value)
        except Exception as e:
            raise UpdateMetricError(f"Metric {metric_name} is not registered.") from e

    def get_metrics(self, metric_name: str) -> Iterable[Metric]:
        """
        Get the value of a metric.
        :param metric_name: Name of the metric.
        :return: Value of the metric.
        """
        try:
            return self.metric_adapters[metric_name.lower()].get_metric()
        except KeyError:
            raise UnknownMetricError(f"Metric {metric_name} is not registered.")
