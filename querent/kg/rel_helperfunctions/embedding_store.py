from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain.docstore.document import Document
from nltk.tokenize import sent_tokenize
import os

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
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', vector_store_path='./querent/kg/rel_helperfunctions/vectorstores/'):
        self.logger = setup_logger("EmbeddingStore_config", "EmbeddingStore")
        try:
            self.model_name = model_name
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
            self.vector_store_path = vector_store_path
            self.db = None
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize EmbeddingStore: {e}")
            raise Exception(f"Failed to initialize EmbeddingStore: {e}")


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

    def as_retriever(self, search_type='similarity', search_kwargs={'k': 2}):
        try:
            if self.db is None:
                raise ValueError("FAISS index is not loaded. Call load_index() first.")
            return self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize retriever: {e}")
            raise Exception(f"Failed to initialize retriever: {e}")
    