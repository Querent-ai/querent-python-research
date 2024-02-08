import json
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain.docstore.document import Document
from nltk.tokenize import sent_tokenize
import os

import requests

from querent.logging.logger import setup_logger

"""
    A class for creating and managing an embedding-based document store using FAISS (Facebook AI Similarity Search).

    This class utilizes sentence-transformer embeddings to vectorize text and store it in a FAISS index for 
    efficient similarity searches. It supports creating the index from a list of texts, saving and loading the 
    index, and retrieving documents based on similarity queries.

    Attributes:
        model_name (str): The name of the model used for generating embeddings. Defaults to 
                          'sentence-transformers/all-MiniLM-L6-v2'.
        embeddings (HuggingFaceEmbeddings): An instance of HuggingFaceEmbeddings for embedding extraction.
        vector_store_path (str): The path to save or load the FAISS index files.
        db (FAISS): The FAISS index instance.

    Methods:
        create_index(texts, verbose=False): Creates a FAISS index from a list of texts.
            Parameters:
                texts (list of str): The texts to be indexed.
                verbose (bool): If True, prints information about the chunks being indexed.

        save_index(file_name='FAISS_index'): Saves the FAISS index to a file.
            Parameters:
                file_name (str): The name of the file to save the index. Defaults to 'FAISS_index'.

        load_index(file_name='FAISS_index'): Loads a FAISS index from a file.
            Parameters:
                file_name (str): The name of the file to load the index. Defaults to 'FAISS_index'.

        as_retriever(search_type='similarity', search_kwargs={'k': 2}): Provides a retriever for performing 
        searches on the index.
            Parameters:
                search_type (str): The type of search to perform ('similarity' or other types supported by FAISS).
                search_kwargs (dict): Additional keyword arguments for the search function.
            Returns:
                A retriever instance configured for the specified search type and parameters.
    """

class EmbeddingStore:
    def __init__(self, inference_api_key=None, model_name='sentence-transformers/all-MiniLM-L6-v2', vector_store_path='./querent/kg/rel_helperfunctions/vectorstores/'):
        self.logger = setup_logger("EmbeddingStore_config", "EmbeddingStore")
        try:
            self.model_name = model_name
            if not inference_api_key:
                self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
            else:
                print("using Inference API--------------------------------------")
                self.API_URL = "https://api-inference.huggingface.co/models/"+ model_name
                self.headers = {"Authorization": f"Bearer {inference_api_key}"}
                self.embeddings = HuggingFaceInferenceAPIEmbeddings(api_key= inference_api_key, model_name=model_name)
            self.vector_store_path = vector_store_path
            self.db = None
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize EmbeddingStore: {e}")
            raise Exception(f"Failed to initialize EmbeddingStore: {e}")

    def query(self,payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        return response.json()
    
    def create_index(self, texts, verbose=False):
        try:
            text_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0)
            final_chunks = []
            for text in texts:
                sentences = sent_tokenize(text)
                current_chunk = ""
                for sentence in sentences:
                    token_count = text_splitter.count_tokens(text=current_chunk + sentence)
                    if token_count > 250:
                        if current_chunk:
                            final_chunks.append(current_chunk)
                        current_chunk = sentence
                    else:
                        current_chunk += (" " + sentence).strip()
                if current_chunk:
                    final_chunks.append(current_chunk)

            docs = [Document(page_content=x) for x in final_chunks]
            self.db = FAISS.from_documents(docs, self.embeddings)

            if verbose:
                for i, chunk in enumerate(final_chunks):
                    self.logger.info("Embedding Store Chunk %i: %s", i, chunk)

            return docs
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to create index: {e}")
            raise Exception(f"Failed to create index: {e}")

    def save_index(self, file_name='FAISS_index'):
        try:
            file_path = os.path.join(self.vector_store_path, file_name)
            os.makedirs(self.vector_store_path, exist_ok=True)
            self.db.save_local(file_path)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to save index: {e}")
            raise Exception(f"Failed to save index: {e}")

    def load_index(self, file_name='FAISS_index'):
        try:
            file_path = os.path.join(self.vector_store_path, file_name)
            self.db = FAISS.load_local(file_path, self.embeddings)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to load index: {e}")
            raise Exception(f"Failed to load index: {e}")

    def as_retriever(self, search_type='similarity', search_kwargs={'k': 10}):
        try:
            if self.db is None:
                raise ValueError("FAISS index is not loaded. Call load_index() first.")
            return self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize retriever: {e}")
            raise Exception(f"Failed to initialize retriever: {e}")
    
    def get_embeddings(self, texts):
        try:
            embeddings = []
            for text in texts:
                if isinstance(self.embeddings,HuggingFaceEmbeddings) or isinstance(self.embeddings, HuggingFaceInferenceAPIEmbeddings) :
                    embedding = self.embeddings.embed_query(text)
                    embeddings.append(embedding)
                else:
                    payload = {"inputs": text}
                    embedding = self.query(payload)
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to generate embeddings: {e}")
            raise Exception(f"Failed to generate embeddings: {e}")
    
    
    def generate_embeddings(self, payload):
        try:
            triples = payload
            processed_pairs = []

            for entity, json_string, related_entity in triples:
                data = json.loads(json_string)
                context = data.get("context", "")
                predicate = data.get("predicate","")
                predicate_type = data.get("predicate_type","")
                subject_type = data.get("subject_type","")
                object_type = data.get("object_type","")
                context_embeddings = self.get_embeddings([context])[0]
                essential_data = {
                    "context": context,
                    "context_embeddings" : context_embeddings,
                    "predicate_type": predicate_type,
                    "predicate" : predicate,
                    "subject_type": subject_type,
                    "object_type": object_type
                }
                updated_json_string = json.dumps(essential_data)
                processed_pairs.append((entity, updated_json_string, related_entity))

            return processed_pairs

        except Exception as e:
            self.logger.error(f"Error in extracting embeddings: {e}")
            raise Exception(f"Error in extracting embeddings: {e}")

    