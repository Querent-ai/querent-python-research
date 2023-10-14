from pyshacl import validate
from typing import Dict, Union
from rdflib import RDF, RDFS, Namespace, XSD
import rdflib
from querent.config.graph_config import GraphConfig
from querent.graph.graph import QuerentGraph
from querent.graph.subject import Subject

from querent.graph.utils import URI, BNode, Literal, LiteralType

SH = Namespace("http://www.w3.org/ns/shacl#")


class SHACL(QuerentGraph):
    def __init__(self, config: GraphConfig):
        super().__init__(config)
        self._class_nodes: Dict[str, Union[URI, BNode]] = {}
        self.bind("sh", SH)

    def add_ontology(self, onto_graph):
        converter = SHACLOntoConverter(self._class_nodes)
        self.graph += converter.convert_ontology(onto_graph)._g
        self._class_nodes.update(converter.class_nodes)

    def validate(self, data_graph, onto_graph=None, inference=None):
        if isinstance(data_graph, QuerentGraph):
            data_graph = data_graph._g
        if isinstance(onto_graph, QuerentGraph):
            onto_graph = onto_graph._g
        if onto_graph and inference:
            conforms, results_graph, results_text = validate(
                data_graph + onto_graph, shacl_graph=self.graph, inference=inference
            )
        else:
            conforms, results_graph, results_text = validate(
                data_graph, shacl_graph=self.graph
            )
        results_graph = QuerentGraph(results_graph)
        return conforms, results_graph


class SHACLOntoConverter:
    def __init__(self, class_nodes: Dict[str, Union[URI, BNode]] = None):
        super().__init__()
        self.onto_graph: rdflib.QuerentGraph = None
        self.graph = QuerentGraph()
        self._class_nodes = class_nodes if class_nodes else {}
        self.graph.bind("sh", SH)

    def cnode(self, class_):
        class_ = str(class_)
        if class_ not in self._class_nodes:
            self._class_nodes[class_] = BNode()
        return self._class_nodes[class_]

    @property
    def class_nodes(self):
        return self._class_nodes

    def convert_ontology(self, onto_graph: QuerentGraph) -> QuerentGraph:
        self.onto_graph = (
            onto_graph._g if isinstance(onto_graph, QuerentGraph) else onto_graph
        )
        # build shacl property-based NodeShape for non-domain-referenced properties
        self._convert_ontology_non_referenced_property()
        # build shacl class-based NodeShape
        # build shacl property path-based blank node for domain-referenced properties
        # for path-based property,
        # we can only add sh:datatype/sh:class based on rdfs:range
        self._convert_ontology_class_node_shape()

        # build shacl property based on owl restriction
        # we can add cardinality to it
        self._convert_ontology_owl_restriction()
        return self.graph

    def _property_shape(self, property_: Union[rdflib.URIRef, str, URI]):
        if isinstance(property_, URI):
            property_ = property_.value
        property_ = rdflib.URIRef(property_)
        p_shape = Subject(BNode())
        p_shape.add_property(URI("sh:path"), URI(property_))
        ranges = list(self.onto_graph.objects(property_, RDFS.range))
        self._build_property_ranges(p_shape, ranges)
        return p_shape

    def _build_property_ranges(self, p_shape, ranges):
        if not ranges:
            return
        if len(ranges) == 1:
            range_ = ranges[0]
            type_ = URI("sh:datatype") if self._is_datatype(range_) else URI("sh:class")
            p_shape.add_property(type_, URI(ranges[0]))
        else:
            or_list = []
            for range_ in ranges:
                range_subject = Subject(BNode())
                type_ = (
                    URI("sh:datatype") if self._is_datatype(range_) else URI("sh:class")
                )
                range_subject.add_property(type_, URI(range_))
                or_list.append(range_subject)
            p_shape.add_property(URI("sh:or"), self._add_list(or_list))

    @staticmethod
    def _is_datatype(uri: rdflib.URIRef):
        if isinstance(uri, rdflib.BNode):
            return False
        return uri.startswith(str(XSD)) or uri.startswith(str(RDF))

    def _convert_ontology_non_referenced_property(self):
        for (p,) in self.onto_graph.query(
            """
          SELECT ?p
          WHERE {
            { ?p a rdfs:Property }
            UNION
            { ?p a owl:ObjectProperty }
            UNION
            { ?p a owl:DatatypeProperty }
            FILTER NOT EXISTS { ?p rdfs:domain ?c }
            FILTER NOT EXISTS { ?c owl:onProperty ?p }
          }
        """
        ):
            p_shape = self._property_shape(p)
            p_shape.add_property(URI("rdf:type"), URI("sh:PropertyShape"))
            self.graph.add_subject(p_shape)

    def _convert_ontology_class_node_shape(self):
        for (c,) in self.onto_graph.query(
            """
          SELECT DISTINCT ?s WHERE {
            {?s a owl:Class}
            UNION
            {?s a rdfs:Class}
            UNION
            {?p rdfs:domain ?s}
            UNION
            {?s rdfs:subClassOf|owl:equivalentClass ?o}
            UNION
            {?os rdfs:subClassOf|owl:equivalentClass ?s FILTER NOT EXISTS {?s a owl:Restriction}}
            FILTER isURI(?s)
          }
        """
        ):
            """
            [ a sh:NodeShape ;
              sh:targetClass ?s ;
              sh:property [ sh:path p ; sh:class class ;] ;]
            """
            node_subject = self._class_shape(c)
            for p in self.onto_graph.subjects(RDFS.domain, c):
                property_subject = self._property_shape(p)
                node_subject.add_property(URI("sh:property"), property_subject)
            self.graph.add_subject(node_subject)

    def _class_shape(self, c):
        node_subject = Subject(self.cnode(c))
        node_subject.add_property(URI("rdf:type"), URI("sh:NodeShape"))
        node_subject.add_property(URI("sh:targetClass"), URI(c))
        return node_subject

    def _convert_ontology_owl_restriction(self):
        for c, p, exact, min_, max_ in self.onto_graph.query(
            """
          SELECT ?c ?p ?exact ?min ?max
          WHERE {
            ?c rdfs:subClassOf|owl:equivalentClass ?res .
            ?res a owl:Restriction ;
                 owl:onProperty ?p .
            OPTIONAL {?res owl:cardinality ?exact}
            OPTIONAL {?res owl:minCardinality ?min}
            OPTIONAL {?res owl:maxCardinality ?max}
          }
        """
        ):
            node_subject = self._class_shape(c)
            property_shape = self._property_shape(p)
            if exact:
                property_shape.add_property(
                    URI("sh:count"), Literal(str(exact), type_=LiteralType.integer)
                )
            if min_:
                property_shape.add_property(
                    URI("sh:minCount"), Literal(str(min_), type_=LiteralType.integer)
                )
            if max_:
                property_shape.add_property(
                    URI("sh:maxCount"), Literal(str(max_), type_=LiteralType.integer)
                )
            ranges = []
            for (r,) in self.onto_graph.query(
                """
              SELECT ?r
              WHERE {
                ?c rdfs:subClassOf|owl:equivalentClass ?res .
                ?res a owl:Restriction ;
                     owl:onProperty ?p ;
                     owl:allValuesFrom|owl:someValuesFrom|owl:hasValue ?r
              }
            """,
                initBindings={"c": c, "p": p},
            ):
                ranges.append(r)
            self._build_property_ranges(property_shape, ranges)
            node_subject.add_property(URI("sh:property"), property_shape)
            self.graph.add_subject(node_subject)

    def _add_list(self, list_):
        """
        (:a :b :c) ===
        [ rdf:first :a ; rdf:rest [ rdf:first :b ; rdf:rest [ rdf:first :c ; rdf:rest rdf:nil]]]
        """
        if not list_:
            return URI("rdf:nil")
        head = Subject(BNode())
        head.add_property(URI("rdf:first"), list_[0])
        head.add_property(URI("rdf:rest"), self._add_list(list_[1:]))
        return head
