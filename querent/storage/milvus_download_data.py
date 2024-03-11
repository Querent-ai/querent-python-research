# from pymilvus import connections, Collection
# import pandas as pd

# # Connect to Milvus
# connections.connect("default", host="localhost", port="19530")

# # Specify the collection name
# collection_name = "pipeline_419956e9d07d45059f9c1e0a836350ab"

# # Load the collection
# collection = Collection(name=collection_name)
# collection.load()

# print("Fields - ", collection.schema.fields)

# # Define the fields you want to download, adjust these based on your collection schema
# output_fields = ["id", "knowledge", "relationship", "document", "embeddings", "sentence"]

# # Retrieve data - adjust approach for large collections
# limit = 10000  # Adjust based on collection size and memory capacity
# results = collection.query(expr="", output_fields=output_fields, limit=limit)

# # Construct the dictionary to ensure correct ordering
# data = []
# for res in results:
#     print("Length:  ", len(res["embeddings"]), "-----------", res["id"])
#     row = {field: res[field] for field in output_fields}
#     data.append(row)

# print("Sentence--------", results[0])
# # Convert to DataFrame and ensure columns are in the specified order directly
# df = pd.DataFrame(data, columns=output_fields)

# # Preprocess 'embeddings' column: Convert lists to comma-separated strings
# df['embeddings'] = df['embeddings'].apply(lambda x: ','.join(map(str, x)) if isinstance(x, list) else x)

# # Preprocess 'sentence' column: Replace actual newlines with "\n" string
# df['sentence'] = df['sentence'].apply(lambda x: x.replace('\n', '\\n').replace('\r', '\\r') if isinstance(x, str) else x)

# # Save to CSV, ensuring UTF-8 encoding
# csv_file_path = "milvus_collection_data.csv"
# df.to_csv(csv_file_path, index=False, encoding='utf-8')

# print(f"Data saved to {csv_file_path}")

# # Disconnect from Milvus
# connections.disconnect("default")
