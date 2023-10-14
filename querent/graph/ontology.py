from rdflib import OWL, RDF
from querent.config.graph_config import GraphConfig

from querent.graph.graph import QuerentGraph


class GraphOntology(QuerentGraph):
    def __init__(self, graph_config: GraphConfig):
        super().__init__(graph_config)

    def is_valid(self, s_types, p, o_types):
        """
        Check if the triple is valid according to the schema
        """
        return True

    def add_subject_ontologies(self, subjects):
        """
        Add a list of subjects to the graph
        :param subjects: List[Subject]
        :return:
        """
        self.add_subjects(subjects)

    @property
    def object_properties(self):
        """
        Return all the defined ObjectProperty
        :return: Set[URIRef]
        """
        properties = []
        for property_ in self.graph.subjects(RDF.type, OWL.ObjectProperty):
            properties.append(property_)
        return set(properties)

    @property
    def datatype_properties(self):
        """
        Return all the defined DatatypeProperty
        :return: Set[URIRef]
        """
        properties = []
        for property_ in self.graph.subjects(RDF.type, OWL.DatatypeProperty):
            properties.append(property_)
        return set(properties)
