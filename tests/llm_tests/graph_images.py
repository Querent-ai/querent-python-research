# import gravis as gv
# import networkx as nx
# import pandas as pd

# df = pd.read_csv('/home/nishantg/Downloads/edges_reduced.csv')
# graph = nx.from_pandas_edgelist(df, 'source', 'target')

# # Step 2: Centrality calculation
# centrality = nx.algorithms.degree_centrality(graph)

# # Community detection
# communities = nx.algorithms.community.greedy_modularity_communities(graph)

# # Assignment of node sizes
# nx.set_node_attributes(graph, centrality, 'size')

# # Assignment of node colors
# colors = ['red', 'blue', 'green', 'orange', 'pink']
# for community, color in zip(communities, colors):
#     for node in community:
#         graph.nodes[node]['color'] = color

# fig = gv.d3(graph, use_node_size_normalization=True, node_size_normalization_max=30,
#             use_edge_size_normalization=True, edge_size_data_source='weight', edge_curvature=0.3,
#             zoom_factor=0.6)
# fig.export_png('graph2.png')