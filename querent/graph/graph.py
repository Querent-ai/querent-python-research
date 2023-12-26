from functools import lru_cache
import threading
from typing import Any
from rdflib import Graph
from rdflib.term import URIRef as RDFLibURIRef
from rdflib.term import BNode as RDFLibBNode
from rdflib.term import Literal as RDFLibLiteral
from querent.config.graph_config import GraphConfig
import time
from querent.graph.graph_namespace import NamespaceManager
from querent.graph.subject import Subject
from querent.graph.utils import URI, BNode, Literal
from rdflib.plugins.sparql import prepareQuery

from querent.logging.logger import setup_logger


class QuerentGraph(object):
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
            identifier=RDFLibURIRef(graph_config.graph_identifier),
            store=graph_config.store,
        )

        self.memory_threshold = graph_config.memory_threshold
        self.format = graph_config.graph_format
        self.flush_on_serialize = graph_config.flush_on_serialize
        self.current_timestamp = time.time()
        self.logger = setup_logger(
            self.__class__.__name__, graph_config.graph_identifier
        )
        self._ns = NamespaceManager(self.graph)
        self.memory_cache = dict()
        self.lock = threading.Lock()

    def bind(self, prefix, namespace, override=True, replace=False):
        self._ns.bind(prefix, namespace, override, replace)

    def __add_subject(self, subjects, local_context=None):
        try:
            if not local_context:
                local_context = set()
            for t in subjects:
                s, p, o = t
                if isinstance(o, Subject) and o not in local_context:
                    local_context.add(o)
                    self.__add_subject(o, local_context)
                    o = o.subject
            # convert triple to RDFLib recognizable format
            triple = self._convert_to_rdflib((s, p, o))
            self.graph.add(triple)
        except Exception as e:
            self.logger.error(f"Failed to add subject: {subjects}")
            raise e

    def add_subjects(self, subjects):
        try:
            with self.lock:
                for s in subjects:
                    self.__add_subject(s)
        except Exception as e:
            self.logger.error(f"Failed to add subjects: {subjects}")
            raise e
        finally:
            self.graph.commit()

    def serialize(self):
        """
        Serialize the graph.

        Returns:
            str: Serialized RDF data.
        """
        try:
            if self.format.lower() in ("ttl", "turtle"):
                b_string = self.graph.serialize(
                    format=self.format,
                    namespace_manager=self._ns,
                )
            elif self.format.lower() == "json-ld":
                b_string = self.graph.serialize(
                    format=self.format,
                    contexts=self._ns,
                )
            else:
                b_string = self.graph.serialize(
                    format=self.format,
                )
            if isinstance(b_string, bytes):
                b_string = b_string.decode("UTF-8")

            if self.flush_on_serialize:
                self.graph.remove((None, None, None))

            return b_string
        except Exception as e:
            self.logger.error("Failed to serialize graph")
            self.logger.error(e)
            raise e

    def parse(self, content):
        try:
            self.graph.parse(data=content, format=self.format)
        except Exception as e:
            raise e

    def _is_rdf_type(self, uri: Any) -> bool:
        try:
            return (
                isinstance(self._resolve_uri(uri), RDFLibURIRef)
                or isinstance(self._resolve_uri(uri), RDFLibBNode)
                or isinstance(self._resolve_uri(uri), RDFLibLiteral)
            )
        except Exception as e:
            self.logger.error(f"Failed to resolve URI: {uri.value}")
            return False

    @lru_cache()
    def _resolve_uri(self, uri: URI) -> RDFLibURIRef:
        """
        Convert a URI object into a RDFLib URIRef, including resolve its context

        :param uri: URI
        :return: rdflib.URIRef
        """
        try:
            return self._ns.parse_uri(uri.value)
        except Exception as e:
            self.logger.error(f"Failed to resolve URI: {uri.value}")
            raise e

    def _convert_to_rdflib(self, triple):
        """
        Convert a Node Quad to RDFLib Quad
        """
        s, p, o = triple
        sub = self._resolve_uri(s) if isinstance(s, URI) else RDFLibBNode(s.value)
        pred = self._resolve_uri(p)
        if isinstance(o, URI):
            obj = self._resolve_uri(o)
        elif isinstance(o, Subject):
            if isinstance(o.subject, URI):
                obj = self._resolve_uri(o.subject)
            else:
                obj = RDFLibBNode(o.subject.value)
        elif isinstance(o, BNode):
            obj = RDFLibBNode(o.value)
        elif isinstance(o, Literal):
            obj = RDFLibLiteral(o.value, o.lang, o.raw_type)
        else:
            raise Exception("Object must be URI, BNode or Literal")

        return (sub, pred, obj)

    def clear(self):
        self.graph.remove((None, None, None))

    @property
    def get_current_memory_usage(self):
        # Calculate the current memory usage
        return self.calculate_memory_usage()

    @lru_cache()
    def calculate_memory_usage(self):
        # Calculate and store the memory usage
        memory_usage = self.calculate_actual_memory_usage()
        self.memory_cache["memory_usage"] = memory_usage
        return memory_usage

    def calculate_actual_memory_usage(self):
        # Calculate the actual memory usage
        return self.graph.serialize(format="nt").__sizeof__()

    def execute_query(self, query_str: str):
        """
        Execute a query. Example usage to get all subjects with specific predicate and object

        graph = QuerentGraph()
        Add few triples and then

        sparql_query = \"""
        SELECT ?subject
        WHERE {
            ?subject <http://example.org/predicate> "Example Object" .
        }
        \"""
        results = querent_graph.execute_query(sparql_query)
        print(results)
        """
        try:
            query = prepareQuery(query_str)
            return list(self.graph.query(query))
        except Exception as e:
            self.logger.error(f"Failed to execute query: {query_str}")
            raise e
