import pytest
from querent.config.metric.prometheus import (
    PrometheusAdapterConfig,
    SupportedMetricType,
)
from querent.metric.adapters.promethus_adapter import PrometheusMetricAdapter
from querent.metric.base_metric_adapter import MetricAdapter
from querent.metric.metric_registry import MetricRegistry


@pytest.fixture
def metric_registry() -> MetricRegistry:
    return MetricRegistry()


@pytest.fixture
def prometheus_adapter() -> MetricAdapter:
    config = PrometheusAdapterConfig(
        job_name="test_job",
        labels=["test_metric"],
        metric_type=SupportedMetricType.GAUGE,
    )
    return PrometheusMetricAdapter(config)


@pytest.mark.asyncio
def test_register_metric(
    metric_registry: MetricRegistry, prometheus_adapter: MetricAdapter
):
    # Test the registration of Prometheus metrics
    metric_registry.register_metric_adapter("test_metric", prometheus_adapter)


@pytest.mark.asyncio
def test_update_metric(
    metric_registry: MetricRegistry, prometheus_adapter: MetricAdapter
):
    metric_registry.register_metric_adapter("test_metric", prometheus_adapter)
    metric_registry.update_metric("test_metric", 20)
    # Check if the metric value is updated correctly
    if isinstance(prometheus_adapter, PrometheusMetricAdapter):
        prom_met_iter = metric_registry.get_metrics("test_metric")
        for prom_met in prom_met_iter:
            assert prom_met.samples[0].value == 20
