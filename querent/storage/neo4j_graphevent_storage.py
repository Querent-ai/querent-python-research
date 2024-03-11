# from neo4j import GraphDatabase

# # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"

# import pandas as pd
# from neo4j import GraphDatabase

# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         self.__uri = uri
#         self.__user = user
#         self.__password = password
#         self.__driver = None
#         try:
#             self.__driver = GraphDatabase.driver(self.__uri, auth=(user, password))
#         except Exception as e:
#             print("Failed to create the driver:", e)
        
#     def close(self):
#         if self.__driver is not None:
#             self.__driver.close()
    
#     def execute_query(self, query, parameters=None):
#         if self.__driver is None:
#             print("Driver not initialized!")
#             return None
#         session = None
#         response = None
#         try:
#             session = self.__driver.session()
#             response = session.write_transaction(self._execute_tx, query, parameters)
#         except Exception as e:
#             print("Query failed:", e)
#         finally:
#             if session is not None:
#                 session.close()
#         return response
    
#     @staticmethod
#     def _execute_tx(tx, query, parameters):
#         result = tx.run(query, parameters)
#         return result.single()

# # Configuration for Neo4j
# neo4j_uri = "neo4j+s://6b6151d7.databases.neo4j.io"  # Change this to your Neo4j instance
# neo4j_user = "neo4j"  # Change to your Neo4j username
# neo4j_password = "m0PKWfVRYrhDUSQsTCqOGBYoGQLmN4d4gkTiOV0r8AE"  # Change to your Neo4j password

# # Initialize Neo4j connection
# neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)

# # Load CSV file
# csv_file_path = '/media/ansh/New_Volume_1/reservoir-gpt/eagle-ford.csv'  # Update this to your CSV file path
# df = pd.read_csv(csv_file_path)
# counter = 1
# # Iterate over the DataFrame and insert data into Neo4j
# for index, row in df.iterrows():
#     print("Counter", counter)
#     counter +=1
#     query = f"""
#     MERGE (n1:`{row['subject_type']}` {{name: $entity1}})
#     MERGE (n2:`{row['object_type']}` {{name: $entity2}})
#     MERGE (n1)-[:`{row['predicate']}` {{
#         sentence: $sentence, 
#         document_id: $document_id, 
#         predicate_type: $predicate_type
#     }}]->(n2)
#     """
#     parameters = {
#         'entity1': row['subject'],
#         'entity2': row['object'],
#         'sentence': row['sentence'],
#         'document_id': row['document_id'],
#         'predicate_type': row['predicate_type']
#     }
#     neo4j_conn.execute_query(query, parameters)

# # Close the Neo4j connection
# neo4j_conn.close()
