from pydantic import BaseModel, Field

class BERTLLMConfig(BaseModel):
    # General Engine Configuration
    name: str = "BERTLLMEngine"
    description: str = "An engine for NER and knowledge graph operations using BERT"
    version: str = "0.0.1"

    # Logger Configuration
    logger: str = "BERTLLM.engine_config"

    # BERTLLM Specific Configuration
    ner_model_name: str = "dbmdz/bert-large-cased-finetuned-conll03-english"
    enable_filtering: bool = False
    filter_params: dict = Field(default_factory=dict)

    class Config:
        # This is to allow for the arbitrary types field configurations like __name__
        arbitrary_types_allowed = True

