from enum import Enum
from pydantic import BaseModel


class SupportedMetricType(str, Enum):
    GAUGE = "gauge"
    COUNTER = "counter"
    HISTOGRAM = "histogram"


class PrometheusAdapterConfig(BaseModel):
    """
    PrometheusAdapterConfig is the configuration for the Prometheus adapter.

    Attributes:
        port (int): The port on which the Prometheus metrics will be exposed.
        job_name (str): The job name associated with your application in Prometheus.
        labels (list): List of label names for Prometheus metrics.
    """

    job_name: str
    labels: list
    metric_type: SupportedMetricType
