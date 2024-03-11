# import pandas as pd
# from sklearn.decomposition import PCA
# import matplotlib.pyplot as plt
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# from sklearn.cluster import KMeans
# from langchain_community.embeddings import HuggingFaceEmbeddings

# # Load the CSV file
# df = pd.read_csv('milvus_collection_data.csv')

# # Convert embeddings from strings to lists (assuming they are stored as strings)
# import ast
# df['embeddings'] = df['embeddings'].apply(ast.literal_eval)


# # Assuming embeddings are already lists of floats
# X = list(df['embeddings'])

# # # Reduce dimensions with PCA
# # pca = PCA(n_components=2)
# # X_reduced = pca.fit_transform(X)

# # # Plot
# # plt.figure(figsize=(10, 6))
# # plt.scatter(X_reduced[:, 0], X_reduced[:, 1])
# # plt.title('PCA of Embeddings')
# # plt.xlabel('Component 1')
# # plt.ylabel('Component 2')

# # # Save the plot as an image file
# # plt.savefig('embeddings_pca_visualization.png')
# # plt.close()  # Close the plot to free up memory
# #------------------------------------------------------------

# # kmeans = KMeans(n_clusters=3, random_state=42)
# # clusters = kmeans.fit_predict(X_reduced)

# # # Plot with different colors for each cluster
# # plt.figure(figsize=(10, 6))
# # scatter = plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=clusters, cmap='viridis')
# # plt.title('PCA of Embeddings with K-Means Clustering')
# # plt.xlabel('Component 1')
# # plt.ylabel('Component 2')

# # # Adding a legend to denote clusters
# # plt.legend(*scatter.legend_elements(), title="Clusters")

# # # Save the plot with a new name indicating clustering
# # plt.savefig('embeddings_pca_clusters.png')
# # plt.close()  # Close the plot to free up memory


# # Function to find the most similar vectors
# def find_most_similar_vectors(query_vector, embeddings, top_k=15):
#     # Calculate cosine similarity
#     similarities = cosine_similarity([query_vector], embeddings)[0]
#     # Get the top_k indices of the most similar vectors
#     most_similar_indices = np.argsort(similarities)[-top_k:]
#     return most_similar_indices, np.sort(similarities)[-top_k:]

# # Example usage
# print("X[1]----------------------------------------------------",df["knowledge"][1])
# print("X[77]---------------------------------------------------", len(X))
# # query_vector = X[1]  # Assuming you want to find vectors similar to the first one
# query_vector = "What is the eagle ford shale reservoir porosity and permeability?"

# model_name = "sentence-transformers/all-MiniLM-L6-v2"
# embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
# emb = embeddings.embed_query(query_vector)


# most_similar_indices, similarities = find_most_similar_vectors(emb, X)
# print("Most similar indices:", most_similar_indices)
# print("Similarities:", similarities)
# print("----------------------------------------")
# print(df["sentence"][242])
# print(df["sentence"][44])
# print(df["sentence"][516])
# print(df["sentence"][514])
# print(df["sentence"][515])
# print(df["sentence"][241])
# print(df["sentence"][513])
# print(df["sentence"][156])