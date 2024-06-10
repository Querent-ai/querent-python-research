# import psycopg2
# from psycopg2 import sql
# from psycopg2.extras import Json

# from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
# import numpy as np

# class DatabaseManager:
#     def __init__(self, dbname, user, password, host, port):
#         self.dbname = dbname
#         self.user = user
#         self.password = password
#         self.host = host
#         self.port = port
#         self.connection = None
    
#     def connect_db(self):
#         try:
#             self.connection = psycopg2.connect(
#                 dbname=self.dbname,
#                 user=self.user,
#                 password=self.password,
#                 host=self.host,
#                 port=self.port
#             )
#             print("Database connection established")
#         except Exception as e:
#             print(f"Error connecting to database: {e}")
    
#     def create_tables(self):
#         create_metadata_table_query = """
#         CREATE TABLE IF NOT EXISTS metadata (
#             id SERIAL PRIMARY KEY,
#             subject VARCHAR(255),
#             subject_type VARCHAR(255),
#             predicate VARCHAR(255),
#             object VARCHAR(255),
#             object_type VARCHAR(255),
#             sentence TEXT,
#             file VARCHAR(255),
#             doc_source VARCHAR(255)
#             );
#         """
        
#         create_embedding_table_query = """
#         CREATE TABLE IF NOT EXISTS embedding (
#             id SERIAL PRIMARY KEY,
#             document_source VARCHAR,
#             file VARCHAR,
#             knowledge TEXT,
#             sentence TEXT,
#             predicate TEXT,
#             embeddings vector(384)
#         );
#         """
        
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")  # Enable pgvector extension
#                 cursor.execute(create_metadata_table_query)
#                 cursor.execute(create_embedding_table_query)
#                 self.connection.commit()
#                 print("Tables created successfully")
#         except Exception as e:
#             print(f"Error creating tables: {e}")
#             self.connection.rollback()
    
#     def insert_metadata(self, subject, subject_type, predicate, object, object_type, sentence, file, doc_source):
#         insert_query = """
#         INSERT INTO metadata (subject, subject_type, predicate, object, object_type, sentence, file, doc_source)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#         RETURNING id;
#         """
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(insert_query, (subject, subject_type, predicate, object, object_type, sentence, file, doc_source))
#                 metadata_id = cursor.fetchone()[0]
#                 self.connection.commit()
#                 return metadata_id
#         except Exception as e:
#             print(f"Error inserting metadata: {e}")
#             self.connection.rollback()
    
#     def insert_embedding(self,document_source, knowledge, sentence, predicate, embeddings, file):
#         insert_query = """
#         INSERT INTO embedding (document_source, file, knowledge, sentence, predicate, embeddings)
#         VALUES (%s, %s, %s, %s, %s, %s);
#         """
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(insert_query, (document_source, file, knowledge, sentence, predicate, embeddings))
#                 self.connection.commit()
#         except Exception as e:
#             print(f"Error inserting embedding: {e}")
#             self.connection.rollback()

#     def close_connection(self):
#         if self.connection:
#             self.connection.close()
#             print("Database connection closed")
    
#     def find_similar_embeddings(self, sentence_embedding, top_k=3, similarity_threshold=0.9):
#         # print("Senetence embeddi            ---", sentence_embedding)
#         emb = sentence_embedding
#         query = f"""
#     SELECT id, 1 - (embeddings <=> '{emb}') AS cosine_similarity
#     FROM public.embedding
#     ORDER BY cosine_similarity DESC
#     LIMIT {top_k};
#     """
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(query, (sentence_embedding, top_k))
#                 results = cursor.fetchall()
#                 for result in results:
#                     print("Result -----------", result)
#                 filtered_results = [result for result in results if result[1] >= similarity_threshold]
#             return filtered_results
#         except Exception as e:
#             print(f"Error in finding similar embeddings: {e}")
#             return []
    
#     def fetch_metadata_by_ids(self, metadata_ids):
#         print("metafataaaa ids-----", metadata_ids)

#         query = """
#         SELECT * FROM public.metadata WHERE id IN %s;
#         """
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(query, (tuple(metadata_ids),))
#                 results = cursor.fetchall()
#                 return results
#         except Exception as e:
#             print(f"Error fetching metadata: {e}")
#             return []
    
#     def traverser_bfs(self, metadata_ids):
#         print("Metadata IDs ---", metadata_ids)
#         if not metadata_ids:
#             return []
#         fetch_query = """
#         SELECT * FROM public.metadata WHERE id IN %s;
#         """
#         incoming_query = """
#         SELECT * FROM public.metadata WHERE object = %s;
#         """
#         outgoing_query = """
#         SELECT * FROM public.metadata WHERE subject = %s;
#         """
        
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute(fetch_query, (tuple(metadata_ids),))
#                 initial_results = cursor.fetchall()

#                 related_results = []
                
#                 # For each row in the initial results, find incoming and outgoing edges
#                 for row in initial_results:
#                     subject = row[1]  # 'subject' is the second column
#                     object = row[4]  # 'object' is the fifth column

#                     # Find incoming edges for the subject
#                     cursor.execute(incoming_query, (subject,))
#                     incoming_edges = cursor.fetchall()
                    
#                     # Find outgoing edges for the object
#                     cursor.execute(outgoing_query, (object,))
#                     outgoing_edges = cursor.fetchall()
#                     related_results.append({
#                         'metadata_id': row[0],
#                         'subject': subject,
#                         'object': object,
#                         'incoming_edges': incoming_edges,
#                         'outgoing_edges': outgoing_edges
#                     })

#                 return related_results

#         except Exception as e:
#             print(f"Error fetching related metadata: {e}")
#             return []

#     def show_detailed_relationship_paths(self, data):
#         for entry in data:
#             print(f"Base Entry: Subject = {entry['subject']}, Object = {entry['object']}")
#             print("Incoming Relationships:")
#             if entry['incoming_edges']:
#                 for edge in entry['incoming_edges']:
#                     print(f"  From {edge[1]} via {edge[3]} (Predicate) to {edge[4]} (Object)")
#                     print(f"    Description: {edge[5]}")
#                     print(f"    Source: {edge[7]}")
#             else:
#                 print("  No incoming relationships found.")
            
#             print("Outgoing Relationships:")
#             if entry['outgoing_edges']:
#                 for edge in entry['outgoing_edges']:
#                     print(f"  From {edge[1]} via {edge[3]} (Predicate) to {edge[4]} (Object)")
#                     print(f"    Description: {edge[6]}")
#                     print(f"    Source: {edge[7]}")
#             else:
#                 print("  No outgoing relationships found.")
#             print("\n -----------------------------------------------------")
    
#     def suggest_queries_based_on_edges(self, data):
#         print("Suggested Queries Based on Relationships:")
#         for entry in data:
#             subject = entry['subject']
#             object = entry['object']

#             # Outgoing edges from the subject
#             if entry['outgoing_edges']:
#                 print(f"From '{object}':")
#                 for edge in entry['outgoing_edges']:
#                     print(f"  Explore '{edge[4]}' related to '{object}' via '{edge[3]}' (outgoing) : id - {edge[0]}")
#             else:
#                 print(f"No outgoing queries suggested for '{object}'.")

#             # Incoming edges to the object
#             if entry['incoming_edges']:
#                 print(f"To '{subject}':")
#                 for edge in entry['incoming_edges']:
#                     print(f"  Explore '{edge[1]}' affecting '{subject}' via '{edge[3]}' (incoming) : id - {edge[0]}")
#             else:
#                 print(f"No incoming queries suggested for '{subject}'.")

#             print("\n")


    
# # Usage example
# if __name__ == "__main__":
#     db_manager = DatabaseManager(
#         dbname="querent_test",
#         user="querent",
#         password="querent",
#         host="localhost",
#         port="5432"
#     )
    
#     db_manager.connect_db()
#     db_manager.create_tables()
    
#     # # Example data insertion
#     # metadata_id = db_manager.insert_metadata(
#     #     subject='the_environmental_sciences_department',
#     #     subject_type='i_org',
#     #     predicate='have_be_advocate_clean_energy_use',
#     #     object='dr__emily_stanton',
#     #     object_type='i_per',
#     #     sentence='This is an example sentence.',
#     #     file='example_file',
#     #     doc_source='example_source'
#     # )
    
#     # db_manager.insert_embedding(
#     #     subject_emb=[0.1, 0.2, 0.3],  # Example vectors
#     #     object_emb=[0.4, 0.5, 0.6],
#     #     predicate_emb=[0.7, 0.8, 0.9],
#     #     sentence_emb=[1.0, 1.1, 1.2],
#     #     metadata_id=metadata_id
#     # )
#     # db_manager.update_database_with_averages()
#     query_1 = "What is gas injection ?"
#     # query_1 = "What is eagle ford shale porosity and permiability ?"
#     # query_1 = "What is austin chalk formation ?"
#     # query_1 = "What type of source rock does austin chalk reservoir have ?"
#     # query_1 = "What are some of the important characteristics of Gulf of Mexico basin ?"
#     # query_1 = "Which wells are producing oil ?"
#     create_emb = EmbeddingStore()
#     query_1_emb = create_emb.get_embeddings([query_1])[0]
# # Find similar embeddings in the database
#     similar_embeddings = db_manager.find_similar_embeddings(query_1_emb, top_k=10)
#     # Extract metadata IDs from the results
#     metadata_ids = [result[0] for result in similar_embeddings] 

# # Fetch metadata for these IDs
#     # metadata_results = db_manager.fetch_metadata_by_ids(metadata_ids)
#     # print(metadata_results) 
#     # traverser_bfs_results = db_manager.traverser_bfs(metadata_ids=metadata_ids)
#     # print(traverser_bfs_results) 
#     # print(db_manager.show_detailed_relationship_paths(traverser_bfs_results))
#     # print(db_manager.suggest_queries_based_on_edges(traverser_bfs_results))
    
    
#     ## Second Query 
#     # print("2nd Query ---------------------------------------------------")
#     # user_choice = [27, 29, 171]
#     # traverser_bfs_results = db_manager.traverser_bfs(metadata_ids=user_choice)
#     # print(traverser_bfs_results) 
#     # print(db_manager.show_detailed_relationship_paths(traverser_bfs_results))
#     # print(db_manager.suggest_queries_based_on_edges(traverser_bfs_results))
#     db_manager.close_connection()
