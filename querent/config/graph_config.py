from rdflib.plugins.stores.memory import SimpleMemory


class GraphConfig:
    def __init__(
        self,
        identifier: str,
        format: str = "ttl",
        schema: str = "",
        flush_on_serialize: bool = False,
        store=SimpleMemory(),
        memory_threshold: int = 1024,
    ):
        """
        Initialize the graph configuration.

        Args:
            graph_identifier (str): The identifier for the graph.
            graph_format (str): The format of the graph.
            store (str): The store for the graph.
            memory_threshold (int): this value is in MB.
            schema (str): The schema for the graph.
        """
        self.graph_identifier = identifier
        self.graph_format = format
        self.store = store
        self.memory_threshold = 1024 * 1024 * memory_threshold
        self.flush_on_serialize = flush_on_serialize
        self.schema = schema
