# from pymilvus import connections, Collection, utility, MilvusException
# from langchain_community.embeddings import HuggingFaceEmbeddings

# class MilvusDB:
#     def __init__(self, alias="default"):
#         self.alias = alias
#         self.collection = None
#         try:
#             connections.connect(alias=alias, host="localhost", port="19530")
#             collections = utility.list_collections()
#             if collections:
#                 print("Connecting to collection:", collections[0])
#                 self.collection = Collection(name=collections[0])
#             else:
#                 print("No collections found. Please create a collection first.")
#         except MilvusException as e:
#             raise ConnectionError(f"Unable to connect to the Milvus database: {str(e)}")
    
#     def create_vector_index(self, index_name, field_name, index_params):
#         try:
#             self.collection.create_index(index_name=index_name,field_name=field_name, index_params=index_params)
#         except MilvusException as e:
#             raise ValueError(f"Failed to create vector index: {str(e)}")
    
#     def create_scalar_index(self, index_name, field_name):
#         try:
#             self.collection.create_index(index_name=index_name,field_name=field_name, params={"index_type": "FLAT"})
#         except MilvusException as e:
#             raise ValueError(f"Failed to create scalar index: {str(e)}")
         
#     def drop_index(self, index_name):
#         try:
#             self.collection.drop_index(index_name=index_name)
#         except MilvusException as e:
#             raise RuntimeError(f"Failed to drop index: {str(e)}")
    
#     def get_collection_details(self):
#         try:
#             schema = self.collection.schema
#             print(f"Schema for collection '{self.collection.name}':")
#             for field in schema.fields:
#                 print(f"  Field Name: {field.name}, Field Type: {field.dtype}, Params: {field.params}")
#             print("---------------------------------------------------------------")
#             self.collection.load()
#             print("Collection details:")
#             print(f"Primary Field: {self.collection.primary_field}")
#             print(f"Partitions: {self.collection.partitions}")
#             print(f"Indexes: {self.collection.indexes}")
#             print(f"The collection '{self.collection.name}' contains {self.collection.num_entities} entities.")
#         except Exception as e:
#             raise RuntimeError(f"Failed to retrieve collection details: {str(e)}")
    
#     def delete_collection(self):
#         try:
#             utility.drop_collection(collection_name=self.collection.name)
#         except MilvusException as e:
#             raise RuntimeError(f"Failed to delete the collection: {str(e)}")

#     def disconnect(self):
#         try:
#             connections.disconnect(alias=self.alias)
#         except MilvusException as e:
#             raise ConnectionError(f"Failed to disconnect: {str(e)}")
    
#     def query(self, query, search_params=None, expr=None, top_k =3):
#         if not isinstance(query, str):
#             raise ValueError("Query must be a string.")
#         if search_params is None:
#             search_params = {
#                 "metric_type": "L2", 
#                 "params": {"nprobe": 10}
#             }
#         try:
#             model_name = "sentence-transformers/all-MiniLM-L6-v2"
#             embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
#             emb = embeddings.embed_query(query)
#             output_fields = ["id", "knowledge", "relationship", "document", "sentence"]
#             results = self.collection.search(
#                 data=[emb], 
#                 anns_field="embeddings", 
#                 param=search_params,
#                 limit=top_k,
#                 expr=expr,
#                 output_fields=output_fields,
#                 consistency_level="Strong"
#             )
#             return results
#         except Exception as e:
#             raise RuntimeError(f"Query failed: {str(e)}")

# def main():
#     # Initialize the MilvusDB class
#     milvus_db = MilvusDB()
#     index_params = {
#         "index_type": "IVF_FLAT",  # Example index type
#         "metric_type": "L2",       # Example metric type
#         "params": {"nlist": 128}   # Example params
#     }
#     try:
#         # Replace 'your_field_name' with the actual field name you want to create an index for
#         milvus_db.create_vector_index("example_index", "embeddings", index_params)
#     except Exception as e:
#         print(f"Error creating index: {e}")

#     # Get collection details
#     try:
#         milvus_db.get_collection_details()
#     except Exception as e:
#         print(f"Error retrieving collection details: {e}")
    
#     try:
#         query = "What is the eagle ford shale reservoir porosity and permeability?"
#         milvus_db.query(query)
#     except Exception as e:
#         print(f"Error performing query: {e}")

#     # Clean up - drop index and disconnect. Comment these out if you don't want to drop the index or disconnect yet.
#     try:
#         # Replace 'your_field_name' with the field name of the index you want to drop
#         milvus_db.drop_index("example_index")
#     except Exception as e:
#         print(f"Error dropping index: {e}")

#     try:
#         milvus_db.disconnect()
#     except Exception as e:
#         print(f"Error disconnecting: {e}")

# if __name__ == "__main__":
#     main()
