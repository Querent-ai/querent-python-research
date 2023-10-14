from typing import List, Union
import json

from rdflib import Literal

from querent.graph.ontology import GraphOntology
from querent.graph.shacl import SHACL
from querent.graph.subject import Subject
from querent.graph.utils import URI


class KGSchema(object):
    def __init__(self, content=None):
        self.ontology = GraphOntology()
        self.shacl = SHACL()
        self.need_convert = False
        if content:
            self.add_schema(content, "querent_default")

    def add_schema(self, content: str, format: str):
        self.need_convert = True
        if format == "querent_default":
            if isinstance(content, dict):
                config = content
            else:
                config = json.loads(content)
            self._add_schema_config(config)
        else:
            self.ontology.parse(content, format)

    def add_shacl(self, content: str, format: str):
        self.shacl.parse(content, format)

    def _merge_ontology(self):
        self.shacl.add_ontology(self.ontology)
        self.need_convert = False

    def validate(self, data_graph, inference=None):
        if self.need_convert:
            self._merge_ontology()
        if inference:
            conforms, results_graph = self.shacl.validate(
                data_graph, self.ontology, inference
            )
        else:
            conforms, results_graph = self.shacl.validate(data_graph)
        return conforms, results_graph

    def _add_schema_config(self, config):
        self.ontology._ns.bind_for_schema_config()
        try:
            for field in config["fields"]:
                t = Subject(URI(field))
                if config["fields"][field]["type"] == "kg_id":
                    t.add_property(URI("rdf:type"), URI("owl:ObjectProperty"))
                elif config["fields"][field]["type"] == "number":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                elif config["fields"][field]["type"] == "date":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                elif config["fields"][field]["type"] == "location":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                    t.add_property(URI("rdf:range"), URI("xsd:string"))
                else:
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                    t.add_property(URI("rdf:range"), URI("xsd:string"))
                if (
                    "description" in config["fields"][field]
                    and config["fields"][field]["description"]
                ):
                    t.add_property(
                        URI("rdf:comment"),
                        Literal(config["fields"][field]["description"]),
                    )
                self.ontology.add_subject(t)
        except KeyError as key:
            print(str(key) + " not in config")

    def is_valid(self, s_types: List[URI], p: URI, o_types: List[URI]) -> bool:
        """
        Check if it's a valid triple by checking the property's domain and range
        :param s_types: the types of the subject
        :param p: the property
        :param o_types: the types of the object
        :return: bool
        """
        return self.ontology.is_valid(s_types, p, o_types)

    @property
    def fields(self) -> List[str]:
        """
        Return a list of all fields that are defined in master config
        """
        return [
            self.ontology._ns.qname(uri)
            for uri in self.ontology.object_properties
            | self.ontology.datatype_properties
        ]
