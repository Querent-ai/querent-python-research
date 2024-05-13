# from neo4j import GraphDatabase
# import matplotlib.pyplot as plt
# # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
# import csv
# import pandas as pd
# from neo4j import GraphDatabase
# import networkx as nx
# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer

# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         self.__uri = uri
#         self.__user = user
#         self.__password = password
#         self.__driver = None
#         self.model = SentenceTransformer('all-MiniLM-L6-v2')
#         try:
#             self.__driver = GraphDatabase.driver(self.__uri, auth=(user, password))
#         except Exception as e:
#             print("Failed to create the driver:", e)
        
#     def close(self):
#         if self.__driver is not None:
#             self.__driver.close()
    
#     def sentence_to_embedding(self, sentence):
#         """Converts a sentence to an embedding"""
#         return self.model.encode(sentence, convert_to_tensor=False)
    
#     def extract_subgraph_to_csv(self, query, tags, output_file):
#         with self.__driver.session() as session:
#             result = session.run(query, tags=list(tags))
#             with open(output_file, 'w', newline='') as file:
#                 writer = csv.writer(file)
#                 # Write headers
#                 writer.writerow(['Node Start', 'Relationship Type', 'Node End'])
                
#                 for record in result:
#                     node_start = record["n"]["name"]
#                     node_end = record["m"]["name"]
#                     if isinstance(record["r"], list):  # Handling multiple relationships
#                         for rel in record["r"]:
#                             writer.writerow([node_start, rel.type, node_end])
#                     else:  # Handling a single relationship
#                         writer.writerow([node_start, record["r"].type, node_end])
    
#     def fetch_triples(self, knowledge):
#         subject, relationship, obj = knowledge.split('-')
#         subject = subject
#         obj = obj
#         relationship = relationship
#         query = """
#     MATCH (n)-[r]->(m)
#     WHERE type(r) = $relationship AND n.name = $subject AND m.name = $object
#     RETURN n.name, m.name
#     """
#         with self.__driver.session() as session:
#             result = session.run(query, subject=subject, relationship=relationship, object=obj)
#             nodes = set()
#             for record in result:
#                 nodes.add(record['n.name'])
#                 nodes.add(record['m.name'])
#             return list(nodes)

#     def explore_connections(self, node_names, query_sentence, top_n=10, similarity_threshold=0.5):
#         query = """MATCH (n)-[r]->(m)
# WHERE n.name IN $node_names AND m.name IN $node_names AND n <> m
# RETURN n, r, m, r.sentence AS sentence, r.document_id AS document_id, r.predicate_type AS predicate_type, r.score AS score ORDER BY r.score DESC"""
#         output = []

#         with self.__driver.session() as session:
#             result = session.run(query, node_names=node_names)
#             df = pd.DataFrame([{'Node Start': record['n']['name'],
#                                 'Relationship Type': record['r'].type,
#                                 'Node End': record['m']['name'],
#                                 'Sentence': record['r']['sentence'],
#                                 'Document ID': record['r']['document_id'],
#                                 'Predicate Type': record['r']['predicate_type'],
#                                 'Score': record['r']['score']} for record in result])

#         print("DF:", df)
#         # Sanitize column names
#         df.columns = [col.strip() for col in df.columns]
        
#         # Group by relationship and take top N by score
#         df_top_n = df.groupby(['Node Start', 'Relationship Type', 'Node End']).head(top_n)
        
#         # Now apply select_dominant_sentence for each group
#         df_top_n_unique = df_top_n.groupby(['Node Start', 'Relationship Type', 'Node End', 'Document ID', 'Predicate Type']).agg({'Sentence': self.select_dominant_sentence, 'Score': 'mean'}).reset_index()

#         # Convert sentences to embeddings
#         query_embedding = self.sentence_to_embedding(query_sentence)
#         df_top_n_unique['Embedding'] = df_top_n_unique['Sentence'].apply(self.sentence_to_embedding)
            
#         # Calculate cosine similarity and filter
#         df_top_n_unique['Similarity'] = df_top_n_unique['Embedding'].apply(lambda emb: cosine_similarity([query_embedding], [emb])[0][0])
#         df_filtered = df_top_n_unique[df_top_n_unique['Similarity'] >= similarity_threshold]
            
        
        
#         # Convert the DataFrame back to a list of tuples for graph construction
#         for _, row in df_filtered.iterrows():
#             output.append(row.to_dict())

#         # Build the graph
#         G = nx.MultiDiGraph()
#         for data in output:
#             node_start = data['Node Start']
#             node_end = data['Node End']
#             relationship = data['Relationship Type']
#             # Add edge to graph with all properties
#             G.add_edge(node_start, node_end, label=relationship, **data)

#         return output, G

#     def write_to_csv(self, output, filename="output.csv"):
#         with open(filename, 'w', newline='') as file:
#             writer = csv.writer(file)
#             # Include headers for new columns
#             writer.writerow(['Node Start', 'Relationship Type', 'Node End', 'Sentence', 'Document ID', 'Predicate Type', 'Score'])
            
#             for data in output:
#                 # Unpacking data stored in the dictionary format into the CSV
#                 writer.writerow([data['Node Start'], data['Relationship Type'], data['Node End'], 
#                                 data['Sentence'], data['Document ID'], data['Predicate Type'], data['Score']])



#     def draw_graph(self, G, filename="graph.png", figsize=(12, 12)):
#         plt.figure(figsize=figsize)
#         pos = nx.kamada_kawai_layout(G)  # For a better spread
        
#         # Generate a color map for the edges
#         edge_labels = nx.get_edge_attributes(G, 'label')
#         unique_labels = set(edge_labels.values())
#         color_map = plt.cm.rainbow(np.linspace(0, 1, len(unique_labels)))  # Using a color map
#         label_color_map = dict(zip(unique_labels, color_map))
            
#         # Draw the nodes and edges with the color map
#         default_color = 'grey'
#         edge_colors = [label_color_map.get(edge_labels.get(edge, ''), default_color) for edge in G.edges()]

#         # Draw nodes and edges using the color map
#         nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=500, 
#                 edge_color=edge_colors, linewidths=1, font_size=15)
        
#         # Draw edge labels
#         nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
#         # Save the figure
#         plt.savefig(filename)

#     @staticmethod
#     def select_dominant_sentence(sentences):
#         # Ensure it's a list if it's not already
#         if isinstance(sentences, pd.Series):
#             sentences = sentences.tolist()
        
#         # Assuming sentences is now a list of sentence strings
#         dominant_sentence = max(sentences, key=len)  # Start with the longest sentence

#         for sentence in sentences:
#             if all(sentence not in other or sentence == other for other in sentences):
#                 dominant_sentence = max(dominant_sentence, sentence, key=len)

#         return dominant_sentence
     

# # Configuration for Neo4j
# neo4j_uri = "bolt://localhost:7687"  # Change this to your Neo4j instance
# neo4j_user = "neo4j"  # Change to your Neo4j username
# neo4j_password = "password_neo" 

# # Initialize Neo4j connection
# neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
# input_data = {
#   "session_id": "647b459710c54881b464a1b20d5a40f0",
#   "query": "How does the geological variation within the Eagle Ford Shale affect the production outcomes of different wells?",
#   "insights": [
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "carbonate-has_image-hydraulic_fracturing",
#       "sentence": "4.1 geology the shale formation of eagle ford is of the late cretaceous era, roughly 90 million years old. it has a high carbonate content, up to 70%, which makes it brittle and facilitates hydraulic fracturing (texas rrc, 2014). during the cretaceous time the tectonic movements caused the land masses in the south-east, in the direction of the mexican gulf, to be pressed down.",
#       "tags": "carbonate, hydraulic_fracturing, has_image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": "underground slope of the geological layers in texas. the depth of the eagle ford shale varies from the surface to more than 4 km underground. source: eagleford.org (2014)",
#       "tags": "depth, eagle_ford_shale, has_image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": " \n\nt\n\neagle ford shale play, wo\nwestern gulf basin, :\n~~ south texas __.... inal\n\n   \n \n  \n  \n \n\nmies\na sara\ndeg 2\n\nmap dato 'may 29, 2010\n\n \n  \n\n \n\n  \n \n  \n\n \n\neagle ford producing wells (hpd)\n+ ot\n+ cas\neagle ford petroleum windows (ptrohawk, eos, d})\non\nwot gastcondonsate\nry gas\ntop eagle ford subsea depth structure, ft(petrohawk)\neagle ford shale ticknass,ft(eog)\niii one for sat: ausin chak outeropstnris)\n\n   \n\n \n\n \n\n   \n\n \n\n   \n\n \n\f",
#       "tags": "depth, eagle_ford_shale, has_image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "permeability-has_image-porosity",
#       "sentence": "the wells are located in two counties in different parts of the eagle ford region and there is big chance other parameters than the api gravity differ between the counties. such parameters could be permeability, porosity, brittleness (ability to induce fractures) and other geological parameters. if the porosity is higher more water will be used in the hydro-fracturing and more of fracturing water would stay in the reservoir.",
#       "tags": "permeability, porosity, has_image"
#     }
#   ]
# }

# # Extract tags
# tags = set()
# for insight in input_data["insights"]:
#     tags.update(insight["tags"].split(", "))

# print("Tags for graph query:", tags)



# output_file = "subgraph_output.csv"
# # Every Relationsip
# query1 = """
#         MATCH (n)-[r]->(m)
#         WHERE n.name IN $tags AND m.name IN $tags
#         RETURN n, r, m
#         """
# subgraph_data = neo4j_conn.extract_subgraph_to_csv(query1, tags, output_file)
# print(subgraph_data)

# knowledge_items = [insight['knowledge'] for insight in input_data['insights']]
# nodes = set()
# for knowledge in knowledge_items:
#     print("Knowledge----", knowledge)
#     nodes.update(neo4j_conn.fetch_triples(knowledge))

# print("Nodes for graph query:", nodes)
# subgraph_data, graph = neo4j_conn.explore_connections(list(nodes), query_sentence="What is eagle ford shale reservoir porosity and permeability ?")
# # print(subgraph)
# neo4j_conn.write_to_csv(subgraph_data,  "my_subgraph_data.csv")
# neo4j_conn.draw_graph(graph)

# neo4j_conn.close()
