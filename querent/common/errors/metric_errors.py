# UnknownMetricError(f"Unknown metric: {metric_name}")
class MetricError:
    UNKNOWNMETRICERROR = "Unknown Metric Error"


class UnknownMetricError(Exception):
    def __init__(self, message=None) -> None:
        super().__init__(message)
        self.error_code = MetricError.UNKNOWNMETRICERROR