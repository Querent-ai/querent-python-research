from collections import Counter
from typing import Iterable
from prometheus_client import (
    CollectorRegistry,
    Gauge,
    Histogram,
    Metric,
)
from querent.config.metric.prometheus import (
    PrometheusAdapterConfig,
    SupportedMetricType,
)
from querent.metric.base_metric_adapter import MetricAdapter


class PrometheusMetricAdapter(MetricAdapter):
    def __init__(self, config: PrometheusAdapterConfig):
        self.job_name = config.job_name
        self.labels = config.labels
        self.metric_type = config.metric_type
        self.registry = CollectorRegistry()
        self.metric = None
        self._set_metric(config.metric_type)

    def get_labels(self) -> list:
        return self.labels

    def get_metric(self) -> Iterable[Metric]:
        return self.registry.collect()

    def update_metric(self, metric_value: int):
        if self.metric_type == SupportedMetricType.GAUGE:
            self.metric.labels(self.labels).set(metric_value)
        elif self.metric_type == SupportedMetricType.COUNTER:
            self.metric.labels(self.labels).inc(metric_value)
        elif self.metric_type == SupportedMetricType.HISTOGRAM:
            self.metric.labels(self.labels).observe(metric_value)
        else:
            raise ValueError(f"Metric type {self.metric_type} is not supported.")

    def _set_metric(self, metric_type: str):
        if metric_type == SupportedMetricType.GAUGE:
            self.metric = Gauge(
                self.job_name, "Metric", self.labels, registry=self.registry
            )
        elif metric_type == SupportedMetricType.COUNTER:
            self.metric = Counter(
                self.job_name, "Metric", self.labels, registry=self.registry
            )
        elif metric_type == SupportedMetricType.HISTOGRAM:
            self.metric = Histogram(
                self.job_name, "Metric", self.labels, registry=self.registry
            )
        else:
            raise ValueError(f"Metric type {metric_type} is not supported.")
