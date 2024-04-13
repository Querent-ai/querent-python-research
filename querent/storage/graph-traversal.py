import pandas as pd
import networkx as nx

def load_data(csv_file):
    # Load the CSV data into a DataFrame
    return pd.read_csv(csv_file)

def build_graph(data):
    
    G = nx.DiGraph()  # Use DiGraph for directed graph; use Graph for undirected graph
    for _, row in data.iterrows():
        # Adding nodes with attributes for types
        G.add_node(row['subject'], node_type=row['subject_type'])
        G.add_node(row['object'], node_type=row['object_type'])
        
        # Adding edge with attributes for predicate and sentence
        G.add_edge(row['subject'], row['object'], predicate=row['predicate'],
                   predicate_type=row['predicate_type'], sentence=row['sentence'])
    return G

def display_edges(G):
    for u, v, data in G.edges(data=True):
        print(f"From {u} to {v} with attributes {data}")

def find_shortest_path(G, start_node, end_node):
    try:
        # This will consider the 'weight' attribute to find the shortest path
        path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
        return path
    except nx.NetworkXNoPath:
        return "No path exists between these nodes."

def bfs_traversal(G, start_node):
    # Returns a generator of nodes in a breadth-first traversal
    return list(nx.bfs_edges(G, start_node))

def process_query(graph, start, end, method='dijkstra'):
    """Process a query and update the graph based on the path used."""
    if method == 'dijkstra':
        path = nx.dijkstra_path(graph, start, end, weight='weight')
    elif method == 'bfs':
        path = nx.shortest_path(graph, start, end)  # BFS for unweighted shortest path
    elif method == 'all_paths':
        paths = list(nx.all_simple_paths(graph, start, end))
        # You might choose the most direct path, the shortest, or another criterion
        path = min(paths, key=len)  # Example: choosing the shortest path by number of edges

    # Update weights based on the chosen path
    update_edge_weights(graph, path)

    return path

def update_edge_weights(graph, path):
    """Decrease weight of edges in the path to prioritize them in future searches."""
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        if 'weight' in graph[u][v]:
            # Decreasing the weight by a factor, e.g., making it 90% of the current weight each time
            graph[u][v]['weight'] *= 0.9
        else:
            graph[u][v]['weight'] = 1  # Initialize weight if not present
    
def main(csv_file, start_node, end_node):
    data = load_data(csv_file)
    graph = build_graph(data)
    path, predicates = find_shortest_path(graph, start_node, end_node)
    if isinstance(path, list):  # Check if a path was found
        print("Shortest path from", start_node, "to", end_node, ":", path)
        print("Predicates on the path:", predicates)
    else:
        print(path)  # Print the error message if no path was found


if __name__ == "__main__":
    csv_file = '/media/ansh/New_Volume_1/reservoir-gpt/eagle-ford.csv'  # Update this path to your CSV file location
    start_node = 'temperature'        # Customize to your data
    end_node = 'permeability'            # Customize to your data
    main(csv_file, start_node, end_node)