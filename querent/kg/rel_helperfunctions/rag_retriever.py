from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from sentence_transformers import CrossEncoder


class RAGRetriever:
    def __init__(self, faiss_index_path, emb_model_name, embedding_store, logger):
        self.faiss_index_path = faiss_index_path
        self.emb_model_name = emb_model_name
        self.cross_encoder = self.load_cross_encoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
        self.create_emb = embedding_store
        self.logger = logger
    
    def load_cross_encoder(self, model_name):
        return CrossEncoder(model_name)
    
    def build_faiss_index(self, data):
        try:
            contexts = set()
            for item in data:
                if isinstance(item, tuple) and len(item) == 3:
                    _, predicate_dict, _ = item
                    if isinstance(predicate_dict, dict) and 'context' in predicate_dict:
                        context = predicate_dict['context']
                        context = context.encode().decode('unicode_escape')
                        contexts.add(context)
            self.create_emb.create_index(texts=contexts, verbose=True)
            self.create_emb.save_index('my_FAISS_index')
        except Exception as e:
            self.logger.error(f"Error in building FAISS index: {e}")
            raise Exception(f'Error in building FAISS Index : {e}')


    
    def load_faiss_index(self):
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=self.emb_model_name,
                model_kwargs={'device': 'cpu'}
            )
            db = FAISS.load_local(self.faiss_index_path, embeddings)
            return db
        except Exception as e:
            self.logger.error(f"Error loading FAISS Index: {e}")
            raise Exception(f"Error loading FAISS Index: {e}")

    

    def setup_retriever(self, db, search_type_user=None, search_kwargs={'k': 10}):
        try:
            if search_type_user is not None:
                retriever = db.as_retriever(
                    search_type=search_type_user,
                    search_kwargs=search_kwargs
                )
            else:
                retriever = db.as_retriever(
                    search_kwargs=search_kwargs
                )
            return retriever
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error setting up retriever: {e}")
            raise Exception(f"Error setting up retriever: {e}")

    def rerank_documents(self, documents, query, top_k=3):
        document_texts = [doc.page_content for doc in documents]
        pairs = [[query, text] for text in document_texts]
        scores = self.cross_encoder.predict(pairs)
        ranked_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked_docs[:top_k]]

    def retrieve_documents(self, db, prompt , search_type_user=None, search_kwargs={'k': 10}):
        try:
            self.qa_llm = self.setup_retriever(db, search_type_user=search_type_user, search_kwargs=search_kwargs)
            retrieved_docs = self.qa_llm.get_relevant_documents(prompt)
            top_docs = self.rerank_documents(retrieved_docs, prompt)
            return top_docs
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error asking questions to LLM: {e}")
            raise Exception(f"Error asking LLM: {e}")
