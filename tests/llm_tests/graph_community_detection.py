# import community as community_louvain
# import matplotlib.cm as cm
# import matplotlib.pyplot as plt
# import networkx as nx
# import pandas as pd
# # Apply the Louvain algorithm for community detection
# data_reduced = pd.read_csv('/home/nishantg/Downloads/edges_reduced.csv')

# # Create a directed graph from the dataset
# G = nx.from_pandas_edgelist(data_reduced, source='source', target='target', edge_attr=True, create_using=nx.DiGraph())
# G_undirected = G.to_undirected()

# # Apply community detection
# partition = community_louvain.best_partition(G_undirected)

# # Visualization (optional)
# pos = nx.spring_layout(G_undirected)  # Layout for undirected graph
# cmap = cm.get_cmap('viridis', max(partition.values()) + 1)
# nx.draw_networkx_nodes(G_undirected, pos, partition.keys(), node_size=40,
#                        cmap=cmap, node_color=list(partition.values()))
# nx.draw_networkx_edges(G_undirected, pos, alpha=0.5)
# # After your plotting code
# plt.savefig('community_detection.png')
