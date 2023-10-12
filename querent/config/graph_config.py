class GraphConfig:
    def __init__(
        self,
        graph_name: str,
        graph_format: str,
        flush_on_stream: bool,
        store: str = "IOMemory",
        memory_threshold: int = 1024,
        callback_interval=None,
    ):
        """
        Initialize the graph configuration.

        Args:
            graph_name (str): The name of the graph.
            graph_format (str): The format of the graph.
            store (str): The store for the graph.
            memory_threshold (int): this value is in MB.
        """
        self.graph_name = graph_name
        self.graph_format = graph_format
        self.store = store
        self.memory_threshold = 1024 * 1024 * memory_threshold
        self.flush_on_stream = flush_on_stream
        self.callback_interval = callback_interval
