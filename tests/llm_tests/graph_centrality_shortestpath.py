# import pandas as pd
# import networkx as nx

# # Load the CSV file to create a graph
# data_reduced = pd.read_csv('/home/nishantg/Downloads/edges_reduced.csv')

# # Create a directed graph from the dataset
# G = nx.from_pandas_edgelist(data_reduced, source='source', target='target', edge_attr=True, create_using=nx.DiGraph())

# # Compute Centrality Measures
# degree_centrality = nx.degree_centrality(G)
# betweenness_centrality = nx.betweenness_centrality(G)
# closeness_centrality = nx.closeness_centrality(G)
# eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)

# # Identify the two most central nodes
# most_central_nodes = sorted(degree_centrality.items(), key=lambda item: item[1], reverse=True)[:2]
# node1, node2 = most_central_nodes[0][0], most_central_nodes[1][0]

# # Find the shortest path between the two most central nodes
# shortest_path = nx.shortest_path(G, source=node1, target=node2)

# # Display the results
# print(f"Degree Centrality: {degree_centrality}")
# print(f"Betweenness Centrality: {betweenness_centrality}")
# print(f"Closeness Centrality: {closeness_centrality}")
# print(f"Eigenvector Centrality: {eigenvector_centrality}")
# print(f"Most Central Nodes: {most_central_nodes}")
# print(f"Shortest Path Between Most Central Nodes: {shortest_path}")
