from typing import List, Union
import json
from querent.config.graph_config import GraphConfig
from querent.graph.errors import BadSchemaException

from querent.graph.ontology import GraphOntology
from querent.graph.shacl import SHACL
from querent.graph.subject import Subject
from querent.graph.utils import URI, BNode, Literal
from querent.logging.logger import setup_logger


class KGSchema(object):
    def __init__(self, config: GraphConfig):
        self.ontology = GraphOntology(config)
        self.shacl = SHACL(config)
        self.schema_enabled = False
        self.logger = setup_logger("schema", config.schema.encode())
        if config.schema:
            self.add_schema(config.schema, "querent_default")

    def add_schema(self, schema: str, format: str):
        try:
            self.schema_enabled = True
            if format == "querent_default":
                if isinstance(schema, dict):
                    schema = schema
                else:
                    schema = json.loads(schema)
                self._add_schema_config(schema)
            else:
                self.ontology.parse(schema, format)
        except Exception as e:
            raise BadSchemaException(e)

    def add_shacl(self, content: str, format: str):
        self.shacl.parse(content, format)

    def _merge_ontology(self):
        self.shacl.add_ontology(self.ontology)
        self.schema_enabled = False

    def validate(self, data_graph, inference=None):
        if self.schema_enabled:
            self._merge_ontology()
        if inference:
            conforms, results_graph = self.shacl.validate(
                data_graph, self.ontology, inference
            )
        else:
            conforms, results_graph = self.shacl.validate(data_graph)
        return conforms, results_graph

    def _add_schema_config(self, schema):
        self.ontology._ns.bind_for_schema_config()
        try:
            for field in schema["fields"]:
                t = Subject(URI(field))
                if schema["fields"][field]["type"] == "id":
                    t.add_property(URI("rdf:type"), URI("owl:ObjectProperty"))
                elif schema["fields"][field]["type"] == "number":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                elif schema["fields"][field]["type"] == "date":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                elif schema["fields"][field]["type"] == "location":
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                    t.add_property(URI("rdf:range"), URI("xsd:string"))
                else:
                    t.add_property(URI("rdf:type"), URI("owl:DatatypeProperty"))
                    t.add_property(URI("rdf:range"), URI("xsd:string"))
                if (
                    "description" in schema["fields"][field]
                    and schema["fields"][field]["description"]
                ):
                    t.add_property(
                        URI("rdf:comment"),
                        URI(schema["fields"][field]["description"]),
                    )
                self.ontology.add_subject_ontologies([t])
        except Exception as e:
            self.logger.error(f"Error adding schema config: {e}")

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
