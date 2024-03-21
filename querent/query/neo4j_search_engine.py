from neo4j import GraphDatabase
import networkx as nx

class Neo4jQuery:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def parse_milvus_search_results(self, search_results):
        print(type(search_results))
        sentences = []
        for hit_str_list in search_results:
            for hit in hit_str_list:
                entity = hit.entity
                sentence = entity.get('sentence')
                if sentence:
                    sentences.append(sentence)

        return sentences

    def query_subgraph(self, sentences, output_file="result.graphml", query = (
            "MATCH (a)-[r]->(b) "
            "WHERE r.sentence CONTAINS $sentence "
            "RETURN a, r, b"
        )):
        with self.driver.session() as session:
            for sentence in sentences:
                result = session.read_transaction(self._find_subgraph, sentence, query)
                print("---------------------------------")
                for record in result:
                    print(record)
        G = nx.MultiDiGraph()  # Create a directed graph
        with self.driver.session() as session:
            for sentence in sentences:
                result = session.read_transaction(self._find_subgraph, sentence, query)
                for record in result:
                    a, r, b = record["a"], record["r"], record["b"]
                    G.add_node(a.id, **a)  # Add nodes with properties
                    G.add_node(b.id, **b)
                    G.add_edge(a.id, b.id, key=r.type, **dict(r))  # Add edge with properties
        nx.write_graphml(G, output_file)  # Export graph to GraphML file
        print(f"Graph has been exported to {output_file}.")

    @staticmethod
    def _find_subgraph(tx, sentence, query):
        result = tx.run(query, sentence=sentence)
        return [record for record in result]

# Example usage
if __name__ == "__main__":
    # Step 1: Query Milvus and get sentences (this is a simplified representation)
    milvus_results = ['["id: 448246479761452680, distance: 0.40927839279174805, entity: {\'sentence\': \'these experiments will shed light  on the nano-petrophysical properties of the reservoir regarding porosity, pore throat distribution,  permeability, and flow patterns.    mip results from this study show that eagle ford shale has a wide range of pore structure  parameters with porosity values varying from 0.11 to 7.25% and permeability from 0.005 to 11.6  \', \'id\': 448246479761452680, \'knowledge\': \'eagle_ford_shale_has_porosity\', \'relationship\': \'has\', \'document\': \'Nano-petrophysical Characterization of the Oil Window of Eagle Ford Shale from Southwestern to Central Texas_ USA.pdf\'}", "id: 448246479761452684, distance: 0.40927839279174805, entity: {\'sentence\': \'these experiments will shed light  on the nano-petrophysical properties of the reservoir regarding porosity, pore throat distribution,  permeability, and flow patterns.    mip results from this study show that eagle ford shale has a wide range of pore structure  parameters with porosity values varying from 0.11 to 7.25% and permeability from 0.005 to 11.6  \', \'id\': 448246479761452684, \'knowledge\': \'porosity_affects_permeability\', \'relationship\': \'affects\', \'document\': \'Nano-petrophysical Characterization of the Oil Window of Eagle Ford Shale from Southwestern to Central Texas_ USA.pdf\'}", "id: 448246479761452682, distance: 0.40927839279174805, entity: {\'sentence\': \'these experiments will shed light  on the nano-petrophysical properties of the reservoir regarding porosity, pore throat distribution,  permeability, and flow patterns.    mip results from this study show that eagle ford shale has a wide range of pore structure  parameters with porosity values varying from 0.11 to 7.25% and permeability from 0.005 to 11.6  \', \'id\': 448246479761452682, \'knowledge\': \'eagle_ford_shale_has_permeability\', \'relationship\': \'has\', \'document\': \'Nano-petrophysical Characterization of the Oil Window of Eagle Ford Shale from Southwestern to Central Texas_ USA.pdf\'}"]']

    # Step 2: Query Neo4j with the sentences
    neo4j_query = Neo4jQuery("neo4j+s://6b6151d7.databases.neo4j.io", "neo4j", "m0PKWfVRYrhDUSQsTCqOGBYoGQLmN4d4gkTiOV0r8AE")
    sentences = neo4j_query.parse_milvus_search_results(milvus_results)
    neo4j_query.query_subgraph(sentences)
    neo4j_query.close()
