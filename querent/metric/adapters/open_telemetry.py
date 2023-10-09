from querent.config.metric.opentelemetry import OpenTelemetryAdapterConfig
from querent.metric.metric_adapter import MetricAdapter


class OpenTelemetryAdapter(MetricAdapter):
    def __init__(self, config: OpenTelemetryAdapterConfig):
        pass

    def register_metric(self, metric_name, initial_value=0):
        pass

    def update_metric(self, metric_name, value):
        pass