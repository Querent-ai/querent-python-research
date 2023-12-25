from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain
from querent.logging.logger import setup_logger

class QASystem:
    def __init__(self, rel_model_path, rel_model_type):
        self.logger = setup_logger("Question-Answering_config", "Question-Answering")
        try:
                self.rel_model_path = rel_model_path
                self.rel_model_type = rel_model_type
                self.llm = self.load_llm()
        except Exception as e:
                self.logger.error(f"Invalid {self.__class__.__name__} configuration. Initialization failed: {e}")
                raise Exception(f"Initialization failed: {e}")
    
    def load_llm(self):
        try:
            file_path = './querent/kg/rel_helperfunctions/json.gbnf'
            llm = LlamaCpp(model_path=self.rel_model_path, max_tokens=-1, temperature=0,verbose=True,n_ctx=1000,f16_kv=True, grammar_path=file_path)
            return llm
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error loading LLM: {e}")
            raise Exception(f"Error loading LLM: {e}")


    def custom_stuff_chain(self, reordered_docs, llm_chain, query):
        try:
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

    def ask_question(self, prompt, llm_chain, top_docs=None):
        try:
            output = self.custom_stuff_chain(reordered_docs=top_docs, llm_chain=llm_chain, query= prompt)
            return output
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error asking questions to LLM: {e}")
            raise Exception(f"Error asking LLM: {e}")