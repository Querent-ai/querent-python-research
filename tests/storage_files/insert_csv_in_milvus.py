# from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType, Partition
# import pandas as pd
# import csv

# # Configuration
# csv_file_path = '/home/nishantg/Downloads/milvus_collection_data.csv'  # Update this path to your CSV file location
# collection_name = "knowledge_collection12300"
# embedding_dim = 384  # Adjust this according to your actual embedding dimension
# # Connect to Milvus
# connections.connect(host='localhost', port='19530')

# # Assuming the CSV has the following columns: id, knowledge, relationship, document, embeddings
# fields = [
#     FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
#     FieldSchema(name="knowledge", dtype=DataType.VARCHAR, max_length=2550),
#     FieldSchema(name="relationship", dtype=DataType.VARCHAR, max_length=2550),
#     FieldSchema(name="document", dtype=DataType.VARCHAR, max_length=2550),
#     FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=384),
#     # Adjust `dim` based on your actual embeddings size
#     FieldSchema(name="sentence", dtype=DataType.VARCHAR, max_length=2550)
# ]

# schema = CollectionSchema(fields, description="Test collection")
# collection = Collection(name=collection_name, schema=schema, using="default", shards_num=2)

# # Function to convert embeddings from string to list of floats
# def convert_embeddings(embeddings_str):
#     return list(map(float, embeddings_str.strip("[]").split(",")))


# with open(csv_file_path, newline='') as csvfile:
#     csvreader = csv.reader(csvfile, delimiter=',')
#     next(csvreader)  # Skip header row
#     for row in csvreader:
#         id, knowledge, relationship, document, embeddings_str, sentence = row
#         embeddings = convert_embeddings(embeddings_str)
#         mr = collection.insert([[
#             int(id)], [knowledge], [relationship], [document], [embeddings], [sentence
#         ]])
#         print(f"Inserted row with ID: {id}, Milvus IDs: {mr.primary_keys}")

# print("Data insertion complete.")