from pydantic import BaseModel, Field
from typing import Dict

class RelationshipExtractorConfig(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"

    # Shared configurations for relationship extraction and BSM
    model_type = 'llama'
    # model_path: str = './tests/llama-2-7b-chat.Q4_K_M.gguf'  # Used as LLaMA model path in BSM
    model_path: str = './tests/llama-2-7b-chat.Q5_K_M.gguf'  # Used as LLaMA model path in BSM
    # Using a dictionary for multiple templates
    qa_templates: Dict[str, str] = Field(default_factory=lambda: {
        "default": """Use the following pieces of information to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Context: {context}
        Question: {query}
        Only return the helpful answer below and nothing else.
        Helpful answer:""",
        
        "default1": """"Please analyze the provided context and two entities
        Context: {context}
        {query}
        Answer:""",
        
        "bsm_template": """Use the following context to answer the user's question.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Context: {context}
        {format_instructions}
        Question: {query}
        Only return the helpful answer below and nothing else.
        Helpful answer:""",
        "template2": """[Content for template 2]""",
        # Add more templates as needed
    })

    # Method to select a template dynamically
    def get_template(self, template_key: str = "default") -> str:
        return self.qa_templates.get(template_key, self.qa_templates["default"])

    # Specific configurations for relationship extraction
    vector_store_path: str = "./querent/kg/rel_helperfunctions/vectorstores/"
    emb_model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'

    # BSM specific configurations
    bsm_validator_model_path: str = "./tests/vicuna-13b-v1.5.Q4_K_M.gguf"
    bsm_validator_model_type='vicuna'
    bsm_max_new_tokens: int = -1
    bsm_temperature: float = 0.1
    bsm_repetition_penalty: float = 1.7
    bsm_context_length: int = 2000

    # Additional parameter for dynamic sub-tasks
    dynamic_sub_tasks: list = Field(default_factory=list)  # List of sub-tasks that user may provide
    
    rag_approach: bool = False
    
    def get_faiss_index_path(self):
        return self.vector_store_path + "my_FAISS_index"
