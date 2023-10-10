import logging
from logging import LogRecord
from querent.common.errors.metric_errors import UnknownMetricError

from querent.metric.metric_registry import MetricRegistry


class LoggingMetricHandler(logging.Handler):
    def __init__(self, metric_registry: MetricRegistry, level=logging.INFO):
        super().__init__(level)
        self.metric_registry = metric_registry

    def emit(self, record: LogRecord) -> None:
        # Split the log message to extract metric-related information.
        parts = record.msg.split(",")
        metric_name: str = None
        metric_value: int = None

        for part in parts:
            # Assuming the log message contains "M/metric: <metric_name>, V/value: <metric_value>"
            if part.lower().strip().startswith("metric:"):
                metric_name = part.split(":")[1].strip().lower()
            elif part.lower().strip().startswith("value:"):
                metric_value_str = part.split(":")[1].strip().lower()
                if metric_value_str.isdigit():
                    metric_value = int(metric_value_str)

        # Check if metric information was found in the log message.
        if metric_name is not None and metric_value is not None:
            # Check if the metric is registered.
            if metric_name not in self.metric_registry.list_metric_adapters():
                self.logger.error(f"Metric {metric_name} is not registered.")
            # Update the metric value.
            self.metric_registry.update_metric(metric_name, metric_value)
        else:
            # If it's not a metric-related log record, you can handle it as a regular log message.
            super().emit(record)
