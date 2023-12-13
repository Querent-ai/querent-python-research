from querent.graph.utils import URI, BNode
from querent.kg.semantic_knowledge import SemanticKnowledge
import json
from querent.graph.utils import URI, BNode, Literal

"""
    A class for managing a semantic knowledge graph, primarily focusing on handling RDF triples with 
    support for reification and metadata. It allows for the addition, removal, and retrieval of semantic 
    triples associated with various subjects in a structured manner.

    Attributes:
        subjects_dict (dict): A dictionary mapping subject URIs to SemanticKnowledge instances.
        metadata_dict (dict): A dictionary for storing additional metadata (currently unused).
        base_uri (str): The base URI used for constructing URIs from string terms.

    Methods:
        string_to_uri(term):
            Converts a string term to a full URI using the base_uri.
        
        parse_predicate(predicate_str):
            Parses a predicate string in JSON format to extract the 'relationship' key.
        
        add_triple_semantic(s, p_str, o, metadata=None):
            Adds a semantic triple to the graph, with optional metadata and reification.
        
        remove_triple(s, p_str, o):
            Removes a semantic triple from the graph.
        
        feed_input(triples_list):
            Processes a list of triples and feeds them into the graph. The predicate can be a JSON string containing additional metadata.
        
        retrieve_triples():
            Retrieves all triples from the semantic knowledge graph.
    """

class Semantic_KnowledgeGraphManager:
    def __init__(self, base_uri="http://geodata.org/"):
        self.subjects_dict = {}
        self.metadata_dict = {}  # New dictionary for storing metadata
        self.base_uri = base_uri

    def string_to_uri(self, term):
        return URI(self.base_uri + term)
    
    def parse_predicate(self, predicate_str):
        predicate_data = json.loads(predicate_str)
        return predicate_data.get('predicate')
    
    def add_triple_semantic(self, s, p_str, o, metadata=None):
        s_uri = self.string_to_uri(s)
        p_uri = self.string_to_uri(p_str)
        o_uri = self.string_to_uri(o)       
        if s_uri not in self.subjects_dict:
            self.subjects_dict[s_uri] = SemanticKnowledge(s_uri)

        self.subjects_dict[s_uri].add_context(p_uri, o_uri, metadata=metadata, reify=True)

    def remove_triple(self, s, p_str, o):
        s_uri = self.string_to_uri(s)
        p_uri = self.string_to_uri(self.parse_predicate(p_str))
        o_uri = self.string_to_uri(o)

        if s_uri in self.subjects_dict:
            self.subjects_dict[s_uri].remove_context(p_uri, o_uri)

    def feed_input(self, triples_list):
        for s, p, o in triples_list:
            metadata = None
            if isinstance(p, str):
                p_parsed = json.loads(p)
                metadata = {key: p_parsed[key] for key in p_parsed if key != 'predicate'}
                p = p_parsed.get('predicate')          
            self.add_triple_semantic(s, p, o, metadata)
    
    def retrieve_triples(self):
        all_triples = []
        for subject_graph in self.subjects_dict.values():
            all_triples.extend(list(subject_graph))
        return all_triples
