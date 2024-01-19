from querent.config.core.bert_llm_config import BERTLLMConfig

class GPTConfig(BERTLLMConfig):
    name: str = "OPENAIEngine"
    description: str = "An engine for NER using BERT and knowledge graph operations using OPENAI"
    version: str = "0.0.1"
    logger: str = "OPENAI.engine_config"
    ner_model_name: str = "botryan96/GeoBERT"
    rel_model_name: str = "gpt-3.5-turbo-1106"

    def __init__(self, config_source=None, **kwargs):
        declared_keys = set(self.__annotations__.keys())
        
        # Initialize BERTLLMConfig with the config_source and kwargs
        super().__init__(config_source=config_source, **kwargs)

        # Now process additional GPTConfig-specific settings
        if config_source:
            config_data = self.load_config(config_source)
            for config_key, config_value in config_data.items():
                if config_key in declared_keys:
                    setattr(self, config_key, config_value)

        # Apply any additional GPTConfig-specific keyword arguments
        for key, value in kwargs.items():
            if key in declared_keys:
                setattr(self, key, value)
