from querent.common.errors.metric_errors import UnknownMetricError
from querent.metric.metric_adapter import MetricAdapter


class MetricRegistry:
    def __init__(self):
        self.metrics = {}
        self.metric_adapters: dict[str, MetricAdapter] = {}

    def register_metric_adapter(self, metric_adapter: MetricAdapter):
        """
        Register a metric adapter.
        :param metric_adapter: Metric adapter instance.
        """
        self.metric_adapters[metric_adapter.__class__.__name__.lower()] = metric_adapter

    def register_metric(self, metric_name: str, initial_value=0):
        """
        Register a new metric with an optional initial value.
        :param metric_name: Name of the metric.
        :param initial_value: (Optional) Initial value for the metric.
        """
        if self.metric_adapters and self.metric_adapters.__len__() > 0:
            for metric_adapter in self.metric_adapters.values():
                metric_adapter.register_metric(metric_name, initial_value)

        if metric_name in self.metrics:
            raise ValueError(f"Metric '{metric_name}' is already registered.")
        metric_name = metric_name.lower()
        self.metrics[metric_name] = initial_value

    def list_metrics(self):
        """
        List all registered metrics.
        :return: List of metric names.
        """
        return list(self.metrics.keys())

    def update_metric(self, metric_name: str, value: int):
        """
        Update the value of a metric.
        :param metric_name: Name of the metric.
        :param value: New value for the metric.
        """
        if metric_name not in self.metrics:
            raise UnknownMetricError(f"Unknown metric: {metric_name}")
        if self.metric_adapters and self.metric_adapters.__len__() > 0:
            for metric_adapter in self.metric_adapters.values():
                metric_adapter.update_metric(metric_name, value)

        self.metrics[metric_name] = value

    def get_metric_value(self, metric_name):
        """
        Get the current value of a metric.
        :param metric_name: Name of the metric.
        :return: Current value of the metric.
        """
        if metric_name not in self.metrics:
            raise UnknownMetricError(f"Unknown metric: {metric_name}")
        return self.metrics[metric_name]

    def increment_metric(self, metric_name, increment_by=1):
        """
        Increment the value of a metric by a specified amount.
        :param metric_name: Name of the metric.
        :param increment_by: (Optional) Amount to increment the metric by (default is 1).
        """
        if metric_name not in self.metrics:
            raise UnknownMetricError(f"Unknown metric: {metric_name}")
        self.metrics[metric_name] += increment_by
