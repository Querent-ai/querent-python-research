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
        return predicate_data.get('relationship')
    
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
                metadata = {key: p_parsed[key] for key in p_parsed if key != 'relationship'}
                p = p_parsed.get('relationship')          
            self.add_triple_semantic(s, p, o, metadata)
    
    def retrieve_triples(self):
        all_triples = []
        for subject_graph in self.subjects_dict.values():
            all_triples.extend(list(subject_graph))
        return all_triples

    
def main():
    input_data = [('tectonic', '{"context": "study , present evidence paleocene\\u2013eocene thermal maximum ( petm ) record within 543-m-thick ( 1780 ft ) deep-marine section gulf mexico ( gom ) using organic carbon stable isotope biostratigraphic constraint . suggest climate tectonic perturbation upstream north american catchment induce substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition shale interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly thick sedimentary section deep-sea fan gom basin .", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "file_path": "dummy_1_file.txt", "relationship": "1. Tectonic perturbation upstream North American catchment may have induced a substantial response downstream in the Gulf Coastal Plain, ultimately affecting the GOM deep-water basin.\\n            2. The increase in sediment supply during the PETM may have been archived in particularly thick sedimentary sections of the deep-sea fan in the GOM basin."}', 'upstream'), ('basin', '{"context": "suggest climate tectonic perturbation upstream north american catchment induce substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition shale interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly thick sedimentary section deep-sea fan gom basin .", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "upstream", "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "file_path": "dummy_1_file.txt", "relationship": "1. High accommodation deposition shale interval coarse-grained terrigenous material was trapped upstream during the onset of PETM, indicating a significant increase in sediment supply from the upstream North American catchment.\\n            2. The substantial response downstream in the Gulf Coastal Plain suggests that climate and tectonic perturbations upstream in the North American catchment had a profound impact on the GOM basin."}', 'upstream'), ('deposition', '{"context": "suggest climate tectonic perturbation upstream north american catchment induce substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition shale interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly thick sedimentary section deep-sea fan gom basin .", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "upstream", "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "file_path": "dummy_1_file.txt", "relationship": "1. High accommodation deposition in shale interval trapped upstream of onset of Paleocene-Eocene Thermal Maximum (PETM)\\n            2. Considerable increase in sediment supply during PETM, archived particularly thick sedimentary section deep-sea fan Gulf of Mexico Basin."}', 'upstream')]

    graph_manager = Semantic_KnowledgeGraphManager()
    graph_manager.feed_input(input_data)

    triples = graph_manager.retrieve_triples()
    for triple in triples:
        s_uri = triple[0]  # Subject URI
        p_uri = triple[1]  # Predicate URI
        o = triple[2]      # Object (URI or Literal)

        s_str = s_uri.value if isinstance(s_uri, URI) else str(s_uri)
        p_str = p_uri.value if isinstance(p_uri, URI) else str(p_uri)
        o_str = o.value if isinstance(o, URI) else str(o)

        print(f"Triple: (Subject: {s_str}, Predicate: {p_str}, Object: {o_str})")

if __name__ == "__main__":
    main()