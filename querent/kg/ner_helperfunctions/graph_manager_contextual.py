from querent.graph.utils import URI, BNode
from querent.kg.contextual_knowledge import ContextualKnowledge

"""
    A class to manage knowledge graphs using RDFLib and custom ContextualKnowledge.

    This class provides methods to add, remove, and retrieve triples from a knowledge graph.
    Each subject in the graph is associated with an instance of ContextualKnowledge, which 
    stores contextual information about the subject.

    Attributes:
    -----------
    subjects_dict : dict
        A dictionary mapping subjects (as URIs) to their corresponding ContextualKnowledge instances.
    base_uri : str
        The base URI used for constructing URIs for terms in the graph.

    Methods:
    --------
    string_to_uri(term: str) -> URI:
        Converts a string term to a URI using the base URI.
    add_triple(s: str, p: str, o: str):
        Adds a triple (subject, predicate, object) to the knowledge graph.
    remove_triple(s: str, p: str, o: str):
        Removes a triple from the knowledge graph.
    feed_input(triples_list: list):
        Feeds a list of triples into the knowledge graph.
    retrieve_triples() -> list:
        Retrieves all triples from the knowledge graph.
    """

class KnowledgeGraphManager:
    def __init__(self, base_uri="http://geodata.org/"):
        self.subjects_dict = {}
        self.base_uri = base_uri

    def string_to_uri(self, term):
        return URI(self.base_uri + term)
    
    def add_triple_contextual(self, s, p, o):
        s_uri = self.string_to_uri(s)
        p_bnode = BNode(p)
        o_uri = self.string_to_uri(o)
        if s_uri not in self.subjects_dict:
            self.subjects_dict[s_uri] = ContextualKnowledge(s_uri)
        self.subjects_dict[s_uri].add_context(p_bnode, o_uri)

    def remove_triple(self, s, p, o):
        s_uri = self.string_to_uri(s)
        p_bnode = BNode(p)
        o_uri = self.string_to_uri(o)
        if s_uri in self.subjects_dict:
            self.subjects_dict[s_uri].remove_context(p_bnode, o_uri)

    def feed_input(self, triples_list):
        for s, p, o in triples_list:
            self.add_triple_contextual(s, p, o)
    
    def retrieve_triples(self):
        all_triples = []
        for subject_graph in self.subjects_dict.values():
            all_triples.extend(list(subject_graph))
        return all_triples


