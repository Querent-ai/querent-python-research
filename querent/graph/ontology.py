from rdflib import OWL, RDF

from querent.graph.graph import QuerentGraph


class GraphOntology(QuerentGraph):
    def is_valid(self, s_types, p, o_types):
        return True

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
