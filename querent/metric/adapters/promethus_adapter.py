from prometheus_client import CollectorRegistry, Gauge, generate_latest
from querent.config.metric.prometheus import PrometheusAdapterConfig
from querent.metric.metric_adapter import MetricAdapter


class PrometheusMetricAdapter(MetricAdapter):
    def __init__(self, config: PrometheusAdapterConfig):
        self.job_name = config.job_name
        self.port = config.port
        self.labels = config.labels
        # Initialize Prometheus CollectorRegistry and set job_name and port.
        self.registry = CollectorRegistry()
        self.registry._namespace = self.job_name
        self.metric = None

    def register_metric(self, metric_name: str, initial_value=0):
        # Register a Prometheus Gauge metric with the given metric_name.
        # Gauge metrics represent values that can go up and down.
        metric = Gauge(
            metric_name,
            f"Metric: {metric_name}",
            labelnames=self.labels,
            registry=self.registry,
        )
        metric.labels(job_name=self.job_name).set(initial_value)
        self.metric = metric

    def update_metric(self, metric_name: str, value):
        if self.metric is not None:
            self.metric.labels(job_name=self.job_name).set(value)

    def get_prometheus_metrics(self) -> bytes:
        # Generate Prometheus metrics in text format.
        return generate_latest(registry=self.registry)
