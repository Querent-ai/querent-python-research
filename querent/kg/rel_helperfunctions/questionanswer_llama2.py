import json
from llama_cpp import Llama
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
            llm = Llama(model_path=self.rel_model_path, f16_kv=True, n_ctx=1000)
            return llm
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error loading LLM: {e}")
            raise Exception(f"Error loading LLM: {e}")

    def ask_question(self, prompt, llm, grammar=None):
        try:
            # output = self.custom_stuff_chain(reordered_docs=top_docs, llm_chain=llm_chain, query= prompt)
            output = llm.create_completion(prompt=prompt, grammar=grammar)
            return output
        
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Error asking questions to LLM: {e}")
            return {}