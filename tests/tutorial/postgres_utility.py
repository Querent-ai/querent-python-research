import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
import numpy as np

class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.connection = None
    
    def connect_db(self):
        try:
            self.connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print("Database connection established")
        except Exception as e:
            print(f"Error connecting to database: {e}")
    
    def create_tables(self):
        create_metadata_table_query = """
        CREATE TABLE IF NOT EXISTS metadata (
            id SERIAL PRIMARY KEY,
            event_id UUID,
            subject VARCHAR(255),
            subject_type VARCHAR(255),
            predicate VARCHAR(255),
            object VARCHAR(255),
            object_type VARCHAR(255),
            sentence TEXT,
            file VARCHAR(255),
            doc_source VARCHAR(255),
            score FLOAT
        );
        """
        
        create_embedding_table_query = """
        CREATE TABLE IF NOT EXISTS embedding (
            id SERIAL PRIMARY KEY,
            event_id UUID,
            embeddings VECTOR(384)
        );
        """
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")  # Enable pgvector extension
                cursor.execute(create_metadata_table_query)
                cursor.execute(create_embedding_table_query)
                self.connection.commit()
                print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
    
    def insert_metadata(self, event_id, subject, subject_type, predicate, object, object_type, sentence, file, doc_source, score):
        insert_query = """
        INSERT INTO metadata (event_id, subject,  subject_type, predicate, object, object_type, sentence, file, doc_source, score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (event_id, subject, subject_type, predicate, object, object_type, sentence, file, doc_source, score))
                metadata_id = cursor.fetchone()[0]
                self.connection.commit()
                return metadata_id
        except Exception as e:
            print(f"Error inserting metadata: {e}")
            self.connection.rollback()
    
    def insert_embedding(self,event_id, embeddings):
        insert_query = """
        INSERT INTO embedding (event_id, embeddings)
        VALUES (%s, %s);
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (event_id, embeddings))
                self.connection.commit()
        except Exception as e:
            print(f"Error inserting embedding: {e}")
            self.connection.rollback()

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def find_similar_embeddings(self, sentence_embedding, top_k=3, similarity_threshold=0.9):
        # print("Senetence embeddi            ---", sentence_embedding)
        emb = sentence_embedding
        query = f"""
    SELECT id, 1 - (embeddings <=> '{emb}') AS cosine_similarity
    FROM public.embedding
    ORDER BY cosine_similarity DESC
    LIMIT {top_k};
    """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (sentence_embedding, top_k))
                results = cursor.fetchall()
                for result in results:
                    print("Result -----------", result)
                filtered_results = [result for result in results if result[1] >= similarity_threshold]
            return filtered_results
        except Exception as e:
            print(f"Error in finding similar embeddings: {e}")
            return []
    
    def fetch_metadata_by_ids(self, metadata_ids):
        print("metafataaaa ids-----", metadata_ids)

        query = """
        SELECT * FROM public.metadata WHERE id IN %s;
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (tuple(metadata_ids),))
                results = cursor.fetchall()
                return results
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            return []
    
    
# Usage example
if __name__ == "__main__":
    db_manager = DatabaseManager(
        dbname="querent_test",
        user="querent",
        password="querent",
        host="localhost",
        port="5432"
    )
    
    db_manager.connect_db()
    db_manager.create_tables()
    
    # # Example data insertion
    # metadata_id = db_manager.insert_metadata(
    #     subject='the_environmental_sciences_department',
    #     subject_type='i_org',
    #     predicate='have_be_advocate_clean_energy_use',
    #     object='dr__emily_stanton',
    #     object_type='i_per',
    #     sentence='This is an example sentence.',
    #     file='example_file',
    #     doc_source='example_source'
    # )
    
    # db_manager.insert_embedding(
    #     subject_emb=[0.1, 0.2, 0.3],  # Example vectors
    #     object_emb=[0.4, 0.5, 0.6],
    #     predicate_emb=[0.7, 0.8, 0.9],
    #     sentence_emb=[1.0, 1.1, 1.2],
    #     metadata_id=metadata_id
    # )
    # db_manager.update_database_with_averages()
    query_1 = "What is gas injection ?"
    # query_1 = "What is eagle ford shale porosity and permiability ?"
    # query_1 = "What is austin chalk formation ?"
    # query_1 = "What type of source rock does austin chalk reservoir have ?"
    # query_1 = "What are some of the important characteristics of Gulf of Mexico basin ?"
    # query_1 = "Which wells are producing oil ?"
    create_emb = EmbeddingStore()
    query_1_emb = create_emb.get_embeddings([query_1])[0]
# Find similar embeddings in the database
    similar_embeddings = db_manager.find_similar_embeddings(query_1_emb, top_k=10)
    # Extract metadata IDs from the results
    metadata_ids = [result[0] for result in similar_embeddings] 

# Fetch metadata for these IDs
    # metadata_results = db_manager.fetch_metadata_by_ids(metadata_ids)
    # print(metadata_results) 
    # traverser_bfs_results = db_manager.traverser_bfs(metadata_ids=metadata_ids)
    # print(traverser_bfs_results) 
    # print(db_manager.show_detailed_relationship_paths(traverser_bfs_results))
    # print(db_manager.suggest_queries_based_on_edges(traverser_bfs_results))
    
    
    ## Second Query 
    # print("2nd Query ---------------------------------------------------")
    # user_choice = [27, 29, 171]
    # traverser_bfs_results = db_manager.traverser_bfs(metadata_ids=user_choice)
    # print(traverser_bfs_results) 
    # print(db_manager.show_detailed_relationship_paths(traverser_bfs_results))
    # print(db_manager.suggest_queries_based_on_edges(traverser_bfs_results))
    db_manager.close_connection()