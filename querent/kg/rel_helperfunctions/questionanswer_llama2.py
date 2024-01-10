from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import StuffDocumentsChain
from querent.logging.logger import setup_logger

"""
    QASystem is a class designed for a question-answering system, leveraging large language models (LLMs) to process and answer queries. It focuses on integrating a relationship model and custom processing chains to handle various aspects of question-answering.

    Key functionalities include:
    - Initialization with paths and types for the relationship model.
    - Loading of the large language model (LLM) with specific configurations.
    - Execution of a custom processing chain, which integrates document processing and LLM querying.
    - Handling the process of asking questions to the LLM and retrieving answers.

    The class includes error handling and logging mechanisms to ensure robustness and traceability of operations. It's designed to handle complex querying processes by integrating multiple components for document processing and query answering in a cohesive workflow.
    """
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