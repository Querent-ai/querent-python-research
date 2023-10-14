from functools import lru_cache
from rdflib import RDF, Graph, URIRef, Literal
from rdflib.plugins.sparql.processor import SPARQLResult
from querent.common.types.querent_quad import QuerentQuad
from querent.config.graph_config import GraphConfig
import time
from querent.graph.graph_namespace import NamespaceManager
from querent.graph.subject import Subject
from querent.graph.utils import URI, BNode

from querent.logging.logger import setup_logger


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
            identifier=URIRef(graph_config.graph_identifier), store=graph_config.store
        )

        self.memory_threshold = graph_config.memory_threshold
        self.format = graph_config.graph_format
        self.flush_on_serialize = graph_config.flush_on_serialize
        self.current_memory_usage = 0
        self.current_timestamp = time.time()
        self.logger = setup_logger(
            self.__class__.__name__, graph_config.graph_identifier
        )
        self._ns = NamespaceManager(self.graph)

    def bind(self, prefix, namespace, override=True, replace=False):
        self._ns.bind(prefix, namespace, override, replace)

    def add_quad(self, quad: QuerentQuad) -> bool:
        """
        Add knowledge to the graph.

        Args:
            quad (QuerentQuad): The quad to add to the graph.

        """
        try:
            if (
                self.current_memory_usage
                + self.__calculate_memory_usage(
                    quad.subject, quad.predicate, quad.object, quad.context
                )
                > self.memory_threshold
            ):
                self.logger.error("Memory threshold exceeded.")
                return False

            knowlege_seed = Subject(quad.subject)
            knowlege_seed.add_property(quad.predicate, quad.object)

            self.add_subject([knowlege_seed], quad.context)

            self.current_memory_usage += self.__calculate_memory_usage(
                quad.subject, quad.predicate, quad.object, quad.context
            )
            return True
        except Exception as e:
            raise e
        finally:
            self.current_timestamp = time.time()
            self.graph.commit()

    def add_subject(self, subjects, context, local_context=None):
        try:
            if not local_context:
                local_context = set()

            for t in subjects:
                s, p, o = t
                if isinstance(o, Subject) and o not in local_context:
                    local_context.add(o)
                    self.add_subject(o, local_context)
                    o = o.subject

                # convert triple to RDFLib recognizable format
                quad = self._convert_quad_to_rdflib((s, p, o, context))
                self.graph.addN(quads=[quad])
                self.current_memory_usage += self.__calculate_memory_usage(
                    s, p, o, context
                )
        except Exception as e:
            self.logger.error(f"Failed to add subject: {subjects}")
            raise e

    def add_quads(self, quads: list[QuerentQuad]):
        """
        Add knowledge to the graph.

        Args:
            quads (list[QuerentQuad]): The quads to add to the graph.

        """
        try:
            if (
                self.current_memory_usage
                + sum(
                    [
                        self.__calculate_memory_usage(
                            quad.subject, quad.predicate, quad.object, quad.context
                        )
                        for quad in quads
                    ]
                )
                > self.memory_threshold
            ):
                self.logger.error("Memory threshold exceeded.")
                return False

            for quad in quads:
                self.add_subject([quad], quad.context)
                self.current_memory_usage += self.__calculate_memory_usage(
                    quad.subject, quad.predicate, quad.object, quad.context
                )
        except Exception as e:
            raise e

        finally:
            self.current_timestamp = time.time()
            self.graph.commit()

    def remove_quad(self, quad: QuerentQuad):
        """
        Remove knowledge from the graph.

        Args:
            quad (QuerentQuad): The quad to remove from the graph.

        """
        try:
            self.graph.remove((quad.subject, quad.predicate, quad.object))
            self.current_memory_usage -= self.__calculate_memory_usage(
                quad.subject, quad.predicate, quad.object, quad.context
            )
        except Exception as e:
            raise e

    def remove_quads(self, quads: list[QuerentQuad]):
        """
        Remove knowledge from the graph.

        Args:
            quads (list[QuerentQuad]): The quads to remove from the graph.

        """
        try:
            self.graph.remove(quad for quad in quads)
            for quad in quads:
                self.current_memory_usage -= self.__calculate_memory_usage(
                    quad.subject, quad.predicate, quad.object, quad.context
                )
        except Exception as e:
            raise e

    def __calculate_memory_usage(self, subject, predicate, obj, context):
        """
        Calculate the memory usage of a quad.

        Args:
            subject: The subject of the quad.
            predicate: The predicate of the quad.
            obj: The object of the quad.
            context: The context or named graph associated with the quad.
        Returns:
            int: The memory usage of the quad.
        """
        return (
            self.__calculate_memory_usage_of_term(subject)
            + self.__calculate_memory_usage_of_term(predicate)
            + self.__calculate_memory_usage_of_term(obj)
            + self.__calculate_memory_usage_of_term(context)
        )

    def __calculate_memory_usage_of_term(self, term):
        """
        Calculate the memory usage of a term.

        Args:
            term: A term in the quad.

        Returns:
            int: The memory usage of the term.
        """
        if isinstance(term, URIRef):
            return len(str(term)) * 2
        elif isinstance(term, Literal):
            return len(str(term)) * 2
        else:
            return 0

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
                self.current_memory_usage = 0
            return b_string
        except Exception as e:
            raise e

    def parse(self, content):
        try:
            self.graph.parse(data=content, format=self.format)
        except Exception as e:
            raise e

    def _is_rdf_type(self, uri: URI) -> bool:
        if not isinstance(uri, URI):
            return False
        return self._resolve_uri(uri) == RDF.type

    @lru_cache()
    def _resolve_uri(self, uri: URI) -> URIRef:
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

    def _convert_quad_to_rdflib(self, quad: QuerentQuad):
        """
        Convert a Node Quad to RDFLib Quad
        """
        s, p, o, c = quad
        sub = self._resolve_uri(s) if isinstance(s, URI) else BNode(s.value)
        pred = self._resolve_uri(p)
        if isinstance(o, URI):
            obj = self._resolve_uri(o)
        elif isinstance(o, Subject):
            if isinstance(o.subject, URI):
                obj = self._resolve_uri(o.subject)
            else:
                obj = BNode(o.subject.value)
        elif isinstance(o, BNode):
            obj = BNode(o.value)
        else:
            obj = Literal(o.value, o.lang, o.raw_type)

        if isinstance(c, URI):
            con = self._resolve_uri(c)
        elif isinstance(c, Subject):
            if isinstance(c.subject, URI):
                con = self._resolve_uri(c.subject)
            else:
                con = BNode(c.subject.value)
        elif isinstance(c, BNode):
            con = BNode(c.value)
        else:
            raise Exception("Context must be URI or BNode")
        return sub, pred, obj, con

    def clear(self):
        self.graph.remove((None, None, None))
        self.current_memory_usage = 0
