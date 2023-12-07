from langchain.llms import CTransformers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.document_transformers import LongContextReorder
from langchain.chains import StuffDocumentsChain, LLMChain
from querent.logging.logger import setup_logger
from sentence_transformers import CrossEncoder


"""
    The class designed to manage and execute question-answering tasks using a large language model (LLM) and an 
    embedding-based retrieval system.

    This class is responsible for loading and configuring a large language model (LLM) and a FAISS index for 
    document retrieval. It supports asking questions and retrieving answers based on the provided template and 
    search criteria.

    Attributes:
        emb_model_name (str): The name of the embedding model.
        rel_model_type (str): The type of the relationship model.
        rel_model_path (str): The path to the relationship model.
        faiss_index_path (str): The path to the FAISS index.
        template (str): The template used for querying the LLM.
        current_search_kwargs (dict): The current search parameters for the retriever.
        current_search_type_user (str): The current search type used in the retriever.
        llm (CTransformers): The large language model instance.
        db (FAISS): The FAISS database instance.
        qa_llm (Retriever): The retriever instance for the QA system.
        long_context_reorder (LongContextReorder): Instance to handle long context reordering.

    Methods:
        load_llm(): Loads the large language model (LLM).
        load_faiss_index(): Loads the FAISS index for embedding-based retrieval.
        setup_retriever(search_type_user=None, search_kwargs={'k': 2}): Sets up the retriever with the given search type and parameters. 
        custom_stuff_chain(reordered_docs, query): Processes the documents and query using the LLM and returns the output.
        ask_question(prompt, search_type_user=None, search_kwargs={'k': 2}): Asks a question using the given prompt and search parameters, and returns the answer.
    """

class QASystem:
    def __init__(self, emb_model_name, rel_model_path, rel_model_type, faiss_index_path, template):
        self.logger = setup_logger("Question-Answering_config", "Question-Answering")
        try:
                self.emb_model_name = emb_model_name
                self.rel_model_type = rel_model_type
                self.rel_model_path = rel_model_path
                self.faiss_index_path = faiss_index_path
                self.template = template
                self.current_search_kwargs = None
                self.current_search_type_user = None
                self.llm = self.load_llm()
                self.db = self.load_faiss_index()
                self.qa_llm = self.setup_retriever()
                self.long_context_reorder = LongContextReorder()
                self.cross_encoder = self.load_cross_encoder('cross-encoder/ms-marco-TinyBERT-L-2-v2')
                

        except Exception as e:
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Initialization failed: {e}")
                raise Exception(f"Initialization failed: {e}")
    
    def load_cross_encoder(self, model_name):
        return CrossEncoder(model_name)

    def load_llm(self):
        try:
            llm = CTransformers(
                model=self.rel_model_path,
                model_type=self.rel_model_type,
                config={'max_new_tokens': 500, 'temperature': 0.01, 'context_length': 4096}
            )
            return llm
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error loading LLM: {e}")
            raise Exception(f"Error loading LLM: {e}")

    def load_faiss_index(self):
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name=self.emb_model_name,
                model_kwargs={'device': 'cpu'}
            )
            db = FAISS.load_local(self.faiss_index_path, embeddings)
            return db
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error loading FAISS Index: {e}")
            raise Exception(f"Error loading FAISS Index: {e}")
    
    def setup_retriever(self, search_type_user=None, search_kwargs={'k': 10}):
        try:
            if search_type_user is not None:
                retriever = self.db.as_retriever(
                    search_type=search_type_user,
                    search_kwargs=search_kwargs
                )
            else:
                retriever = self.db.as_retriever(
                    search_kwargs=search_kwargs
                )
            self.current_search_kwargs = search_kwargs
            self.current_search_type_user = search_type_user
            return retriever
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error setting up retriever: {e}")
            raise Exception(f"Error setting up retriever: {e}")
    
    def rerank_documents(self, documents, query, top_k=3):
        # Assuming that 'page_content' is an attribute of the Document class
        document_texts = [doc.page_content for doc in documents]
        pairs = [[query, text] for text in document_texts]
        scores = self.cross_encoder.predict(pairs)
        ranked_docs = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked_docs[:top_k]]


    def custom_stuff_chain(self, reordered_docs, llm_chain, query):
        try:
            # prompt = PromptTemplate(
            #     template=self.template, input_variables=["context", "query"]
            # )
            # llm_chain = LLMChain(llm=self.llm, prompt=prompt)
            document_prompt = PromptTemplate(
                input_variables=["page_content"], template="{page_content}"
            )
            document_variable_name = "context"
            chain = StuffDocumentsChain(
                llm_chain=llm_chain,
                document_prompt=document_prompt,
                document_variable_name=document_variable_name
            )
            return chain.run(input_documents=reordered_docs, query=query, return_source_documents=True)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error in starting llm chain: {e}")
            raise Exception(f"Error in starting llm chain: {e}")
    
    def retrieve_documents(self, prompt , search_type_user=None, search_kwargs={'k': 8}):
        try:
            if search_kwargs != self.current_search_kwargs or search_type_user != self.current_search_type_user:
                self.qa_llm = self.setup_retriever(search_type_user=search_type_user, search_kwargs=search_kwargs)
            retrieved_docs = self.qa_llm.get_relevant_documents(prompt)
            top_docs = self.rerank_documents(retrieved_docs, prompt)
            print("top documents", top_docs)
            return top_docs
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error asking questions to LLM: {e}")
            raise Exception(f"Error asking LLM: {e}")

    def ask_question(self, prompt, llm_chain, top_docs=None):
        try:
            #reordered_docs = self.long_context_reorder.transform_documents(retrieved_docs)
            output = self.custom_stuff_chain(reordered_docs=top_docs, llm_chain=llm_chain, query= prompt)
            return output
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error asking questions to LLM: {e}")
            raise Exception(f"Error asking LLM: {e}")
        

# # Example usage:
# if __name__ == "__main__":
#     template = """Use the following pieces of information to answer the user's question.
#     If you don't know the answer, just say that you don't know, don't try to make up an answer.
#     Context:{context}
#     {format_instructions}
#     Question: {query}
#     Only return the helpful answer below and nothing else.
#     Helpful answer:
#     """

#     qa_system = QASystem(
#         rel_model_path='/home/nishantg/querent-main/llama-2-7b-chat.Q4_K_M.gguf',
#         rel_model_type='llama',
#         emb_model_name='sentence-transformers/all-MiniLM-L6-v2',
#         faiss_index_path="/home/nishantg/querent-main/querent/querent/kg/rel_helperfunctions/vectorstores/my_FAISS_index",
#         template=template
#     )

#     prompt = "I would like to define a knowledge graph triple like (Subject, Predicate, Object), do Subject - PETM and Object - Gulf of Mexico show a predicate or a relationship ?"
    
#     # Retrieve documents relevant to the prompt
#     retrieved_docs = qa_system.retrieve_documents(prompt)

#     # Ask a question using the retrieved documents
#     answer = qa_system.ask_question(prompt=prompt, retrieved_docs=retrieved_docs)
    
#     print("--------------------------------")
#     print(answer)


    
    
    # answer = qa_system.ask_question(prompt=prompt, search_type_user='similarity_score_threshold',search_kwargs={'score_threshold': 0.5, 'k': 8})
    # print(answer)
    
    # answer = qa_system.ask_question(prompt=prompt, search_type_user='mmr')
    # print(answer)