from langchain.llms import CTransformers
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.document_transformers import LongContextReorder
from langchain.chains import StuffDocumentsChain, LLMChain


class QASystem:
    def __init__(self, emb_model_name, rel_model_path, rel_model_type, faiss_index_path, template):
        self.emb_model_name = emb_model_name
        self.rel_mode_type = rel_model_type
        self.rel_model_path = rel_model_path
        self.faiss_index_path = faiss_index_path
        self.template = template
        self.current_search_kwargs = None
        self.current_search_type_user = None
        self.llm = self.load_llm()
        self.db = self.load_faiss_index()
        self.qa_llm = self.setup_retriever()
        self.long_context_reorder = LongContextReorder() 

    def load_llm(self):
        llm = CTransformers(
            model=self.rel_model_path,
            model_type=self.rel_mode_type,
            config={'max_new_tokens': 256, 'temperature': 0.01, 'context_length' : 4096}
        )
        
        return llm

    def load_faiss_index(self):
        embeddings = HuggingFaceEmbeddings(
            model_name=self.emb_model_name,
            model_kwargs={'device': 'cpu'}
        )
        db = FAISS.load_local(self.faiss_index_path, embeddings)
    
        return db
    
    def setup_retriever(self, search_type_user=None,search_kwargs={'k': 2}):
        if search_type_user is not None:
            retriever = self.db.as_retriever(
            search_type=search_type_user,
            search_kwargs=search_kwargs
            )
        else :
            retriever = self.db.as_retriever(
            search_kwargs=search_kwargs
            )
        self.current_search_kwargs = search_kwargs
        self.current_search_type_user = search_type_user
        
        return retriever

    def custom_stuff_chain(self, reordered_docs, query):
        prompt = PromptTemplate(
            template=self.template, input_variables=["context", "query"]
        )
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )
        document_variable_name = "context"
        chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name)
        
        return chain.run(input_documents=reordered_docs, query=query, return_source_documents=True)

    def ask_question(self, prompt, search_type_user=None, search_kwargs={'k': 2}):
        if search_kwargs != self.current_search_kwargs or search_type_user != self.current_search_type_user:
            self.qa_llm = self.setup_retriever(search_type_user=search_type_user, search_kwargs=search_kwargs)
        retrieved_docs = self.qa_llm.get_relevant_documents(prompt)
        reordered_docs = self.long_context_reorder.transform_documents(retrieved_docs)
        output = self.custom_stuff_chain(reordered_docs, prompt)
        
        return output
        
# # Example usage:
# if __name__ == "__main__":
#     template = """Use the following pieces of information to answer the user's question.
#     If you don't know the answer, just say that you don't know, don't try to make up an answer.
#     Context: {context}
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

#     prompt = "What is the full form of PETM?"
#     answer = qa_system.ask_question(prompt=prompt, search_kwargs={'k':3})
#     print(answer)
    
    # answer = qa_system.ask_question(prompt=prompt, search_type_user='similarity_score_threshold',search_kwargs={'score_threshold': 0.5, 'k': 2})
    # print(answer)
    
    # answer = qa_system.ask_question(prompt=prompt, search_type_user='mmr', search_kwargs={'k':3})
    # print(answer)