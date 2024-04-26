# from querent.query.milvus_search_engine import MilvusDB
# from querent.query.neo4j_search_engine import Neo4jQuery

# def query_engine(query):
#     # Initialize MilvusDB and perform the search query
#     milvus_db = MilvusDB(collection_name="pipeline_df9a1386b16b425ab23d1acc40006b9a")
#     index_params = {
#         "index_type": "IVF_FLAT",  # Example index type
#         "metric_type": "L2",       # Example metric type
#         "params": {"nlist": 128}   # Example params
#     }
#     try:
#         # Replace 'your_field_name' with the field name of the index you want to drop
#         milvus_db.drop_index("example_index")
#     except Exception as e:
#         print(f"Error dropping index: {e}")
#     try:
#         # Replace 'your_field_name' with the actual field name you want to create an index for
#         milvus_db.create_vector_index("example_index", "embeddings", index_params)
#     except Exception as e:
#         print(f"Error creating index: {e}")
        
#     search_results = milvus_db.query(query)
#     print(search_results)
#     # Initialize Neo4jQuery and query the Neo4j database with the extracted sentences
#     neo4j_query = Neo4jQuery("neo4j+s://6b6151d7.databases.neo4j.io", "neo4j", "m0PKWfVRYrhDUSQsTCqOGBYoGQLmN4d4gkTiOV0r8AE")
#     sentences = neo4j_query.parse_milvus_search_results(search_results)
#     print("Sentences", sentences)
#     neo4j_query.query_subgraph(sentences)
    
#     # Cleanup
#     milvus_db.disconnect()
#     neo4j_query.close()

# if __name__ == "__main__":
#     user_query = "What is the eagle ford shale reservoir porosity and permeability?"
#     query_engine(user_query)
