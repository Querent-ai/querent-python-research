from typing import Dict
from querent.config.graph_config import GraphConfig
from querent.graph.graph import QuerentGraph
from querent.graph.schema import KGSchema
from querent.graph.subject import Subject
from querent.graph.utils import URI, BNode, Literal


class QuerentKG(QuerentGraph):
    """
    Querent Knowledge Graph backed by a default schema and stores knowledge in RDF format.
    """

    def __init__(self, config: GraphConfig):
        super().__init__(config)
        self.schema = KGSchema(config)
        self._fork_namespace_manager()

    def _find_types(self, triples):
        """
        find type in root level
        :param triples:
        :return:
        """
        types = []
        for t in triples:
            s, p, o = t
            if self._is_rdf_type(p):
                if isinstance(o, Subject):
                    continue
                types.append(o)
        return types

    def add_subject_knowledge(self, subjects):
        """
        Add subject knowledge to the graph
        :param subjects: list of subjects
        :return:
        """

        try:
            # TODO do some schema validation for the subject
            self.add_subjects(subjects)
        except Exception as e:
            self.logger.error(f"Error adding quad {subjects} to graph: {e}")
            raise e

    @property
    def value(self) -> Dict:
        """
        Get knowledge graph object
        """
        g = {}
        for p, o in self.graph.predicate_objects():
            _, property_ = self._ns.split_uri(p)
            if property_ not in g:
                g[property_] = list()
            g[property_].append(
                {"key": self.create_key_from_value(o, property_), "value": o.toPython()}
            )
        return g

    def create_key_from_value(self, value, field_name: str):
        key = self.schema.field_type(field_name, value)
        if isinstance(key, URI):
            return key
        if isinstance(key, str) or isinstance(key, Literal):
            key = str(key).strip().lower()
        return key

    def serialize(self):
        return super().serialize()

    def _fork_namespace_manager(self):
        for prefix, ns in self.schema.ontology._ns.namespaces():
            self.bind(prefix, ns)

    def add_types(self, type_):
        s = Subject(URI(self.origin_doc.doc_id))
        p = URI("rdf:type")

        if not isinstance(type_, list):
            type_ = [type_]
        for a_type in type_:
            s.add_property(p, URI(a_type))
        self.add_subject(s)

    def validate(self):
        conforms, result_graph = self.schema.validate(self)
        return conforms, result_graph
