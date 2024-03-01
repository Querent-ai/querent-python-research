# import networkx as nx
# import networkx
# import pandas as pd
# from pyvis.network import Network

# from neo4j import GraphDatabase

# class Neo4jConnection:
    
#     def __init__(self, uri, user, pwd):
#         self.__uri = uri
#         self.__user = user
#         self.__pwd = pwd
#         self.__driver = None
#         try:
#             self.__driver = GraphDatabase.driver(self.__uri, auth=(user, pwd))
#         except Exception as e:
#             print("Failed to create the driver:", e)
        
#     def close(self):
#         if self.__driver is not None:
#             self.__driver.close()
        
#     def query(self, query, parameters=None, db=None):
#         session = None
#         response = []
#         try:
#             session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
#             result = session.run(query, parameters)
#             for record in result:
#                 response.append(record)
#         except Exception as e:
#             print("Query failed:", e)
#         finally:
#             if session is not None:
#                 session.close()
#         return response

# # Configuration for Neo4j
# neo4j_uri = "neo4j+s://76fbc5ab.databases.neo4j.io"  # Change this to your Neo4j instance
# neo4j_user = "neo4j"  # Change to your Neo4j username
# neo4j_password = "Wq2VtRNKw1HFbbjC6eB4Wao5XB2kTHvGjuIbEqfGscs"  # Change to your Neo4j password

# # Initialize Neo4j connection
# conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
# # Your Cypher query
# cypher_query = '''
# MATCH (a)-[r]->(b)
# RETURN a, r, b
# LIMIT 100
# '''

# # Execute the query
# results = conn.query(cypher_query)

# # Now let's visualize the results
# G = nx.Graph()

# for record in results:
#     a, r, b = record['a'], record['r'], record['b']
#     # Get the first label from the node's labels set (there could be more than one label)
#     a_label = list(a.labels)[0] if a.labels else 'NoLabel'
#     b_label = list(b.labels)[0] if b.labels else 'NoLabel'
    
#     # Use the 'name' property as title, if available
#     a_name = a.get('name', 'NoName')
#     b_name = b.get('name', 'NoName')
    
#     G.add_node(a.id, label=a_label, title=a_name, group=1)
#     G.add_node(b.id, label=b_label, title=b_name, group=2)
#     G.add_edge(a.id, b.id, title=type(r).__name__)

# # Close the Neo4j connection
# conn.close()

# # Visualization
# nt = Network("500px", "500px", notebook=False)  # Set notebook to False for non-Jupyter environments
# nt.from_nx(G)
# nt.save_graph("neo4j_graph.html")