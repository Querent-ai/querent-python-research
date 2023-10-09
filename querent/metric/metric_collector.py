from abc import ABC
from querent.common.errors.metric_errors import UnknownMetricError
from querent.metric.metric_registry import MetricRegistry


class MetricCollector(ABC):
    def __init__(self, metric_registry: MetricRegistry):
        self.metric_registry = metric_registry

    def collect(self, metric_name, value: int):
        """
        Update a metric's value or create it if it doesn't exist.
        :param metric_name: Name of the metric.
        :param value: Value of the metric.
        """
        try:
            current_value_str = self.metric_registry.get_metric_value(metric_name)
            current_value = int(current_value_str)
            new_value = current_value + value
        except UnknownMetricError:
            # If the metric doesn't exist, create it with the specified value.
            self.metric_registry.register_metric(metric_name, value)
        else:
            # Update the existing metric's value.
            self.metric_registry.update_metric(metric_name, new_value)
