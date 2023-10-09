class MetricAdapter:
    def __init__(self):
        raise NotImplementedError

    def register_metric(self, metric_name, initial_value=0):
        raise NotImplementedError

    def update_metric(self, metric_name, value):
        raise NotImplementedError
