import asyncio
from rdflib import Graph, URIRef, Literal
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_triples import QuerentTriple
from querent.config.graph_config import GraphConfig
import time


class QuerentGraph:
    """
    A class for managing and manipulating an RDF graph with memory management features.
    """

    def __init__(
        self,
        graph_config: GraphConfig,
    ):
        """
        Initialize a QuerentGraph.

        Args:
            graph_config (GraphConfig): Configuration for the graph.
            memory_threshold_percent (float, optional): Memory threshold as a percentage of max_chunk_size. Default is None.
        """
        self.graph = Graph(
            identifier=URIRef(graph_config.graph_name), store=graph_config.store
        )

        self.memory_threshold = graph_config.memory_threshold
        self.callback_interval = graph_config.callback_interval
        self.callback_trigger_event = asyncio.Event()
        self.current_memory_usage = 0
        self.current_timestamp = time.time()
        self.graph_stream_subscribers: list[EventCallbackInterface] = []

        asyncio.create_task(self.start_callback_timer(self.callback_interval))

    async def start_callback_timer(self, callback_interval):
        while True:
            if time.time() - self.current_timestamp >= callback_interval:
                if self.callback_trigger_event.is_set():
                    self.stream_graph()
                    self.current_timestamp = time.time()
                    self.callback_trigger_event.clear()
                self.current_timestamp = time.time()
            await asyncio.sleep(1)

    def subscribe_to_graph_stream(self, callback: EventCallbackInterface):
        """
        Subscribe to the graph stream.

        Args:
            callback (EventCallbackInterface): The callback to subscribe.
        """
        self.graph_stream_subscribers.append(callback)

    def unsubscribe_from_graph_stream(self, callback: EventCallbackInterface):
        """
        Unsubscribe from the graph stream.

        Args:
            callback (EventCallbackInterface): The callback to unsubscribe.
        """
        self.graph_stream_subscribers.remove(callback)

    def _save(self, file_path):
        """
        Save the graph to a file.

        Args:
            file_path (str): The file path for saving the graph.
        """
        self.graph.serialize(destination=file_path, format="nt")

    def _load(self, data):
        """
        Load data into the graph.

        Args:
            data (str): RDF data to load into the graph.
        """
        self.graph.parse(data=data, format="nt")

    def add_knowledge(self, triple: QuerentTriple):
        """
        Add knowledge to the graph.

        Args:
            triple (QuerentTriple): The triple to add to the graph.

        """
        try:
            self.graph.add(triple)
            self.current_memory_usage += self.calculate_memory_usage(
                triple.subject, triple.predicate, triple.object
            )

            if (
                self.memory_threshold
                and self.current_memory_usage >= self.memory_threshold
            ) or (self.callback_trigger_event.is_set()):
                self.stream_graph()
                self.current_memory_usage = 0
        except Exception as e:
            self.graph.rollback()
            raise e
        finally:
            self.graph.commit()

    def calculate_memory_usage(self, subject, predicate, obj):
        """
        Calculate the memory usage of a triple.

        Args:
            subject: The subject of the triple.
            predicate: The predicate of the triple.
            obj: The object of the triple.

        Returns:
            int: The memory usage of the triple.
        """
        return (
            self.calculate_memory_usage_of_term(subject)
            + self.calculate_memory_usage_of_term(predicate)
            + self.calculate_memory_usage_of_term(obj)
        )

    def calculate_memory_usage_of_term(self, term):
        """
        Calculate the memory usage of a term.

        Args:
            term: A term in the triple.

        Returns:
            int: The memory usage of the term.
        """
        if isinstance(term, URIRef):
            return len(str(term)) * 2
        elif isinstance(term, Literal):
            return len(str(term)) * 2
        else:
            return 0

    def stream_graph(self):
        """
        Serialize the graph and stream data to the callback.
        """
        serialized_data = self.graph.serialize(format="nt")
        for callback in self.graph_stream_subscribers:
            callback.handle_event(
                EventType.RDF_GRAPH_UPDATE,
                EventState(
                    timestamp=time.time(),
                    event_type=EventType.RDF_GRAPH_UPDATE,
                    payload=serialized_data,
                ),
            )

    def serialize(self):
        """
        Serialize the graph.

        Returns:
            str: Serialized RDF data.
        """
        return self.graph.serialize(format="nt")

    def query(self, sparql_query):
        """
        Perform a SPARQL query on the graph.

        Args:
            sparql_query (str): The SPARQL query to execute.

        Returns:
            QueryResult: The result of the SPARQL query.
        """
        return self.graph.query(sparql_query)

    def __len__(self):
        """
        Get the total number of triples in the graph.

        Returns:
            int: To total triples in the graph.
        """
        return self.graph.__len__()
