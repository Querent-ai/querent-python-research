import pytest
from querent.config.metric.prometheus import PrometheusAdapterConfig
from querent.metric.adapters.promethus_adapter import PrometheusMetricAdapter
from querent.metric.metric_adapter import MetricAdapter
from querent.metric.metric_registry import MetricRegistry


@pytest.fixture
def metric_registry() -> MetricRegistry:
    return MetricRegistry()


@pytest.fixture
def prometheus_adapter() -> MetricAdapter:
    config = PrometheusAdapterConfig(
        job_name="test_job", port=9090, labels=["label1", "label2"]
    )
    return PrometheusMetricAdapter(config)


def test_register_metric(
    metric_registry: MetricRegistry, prometheus_adapter: MetricAdapter
):
    # Test the registration of Prometheus metrics
    prometheus_adapter.register_metric("test_metric", 10)


def test_update_metric(
    metric_registry: MetricRegistry, prometheus_adapter: MetricAdapter
):
    # Test updating Prometheus metrics
    prometheus_adapter.register_metric("test_metric", 10)
    prometheus_adapter.update_metric("test_metric", 20)
    # Check if the metric value is updated correctly
    if isinstance(prometheus_adapter, PrometheusMetricAdapter):
        prom_met_bytes = prometheus_adapter.get_prometheus_metrics()
        assert b"test_metric 20.0" in prom_met_bytes
