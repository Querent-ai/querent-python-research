from transformers import AutoTokenizer
from querent.kg.contextual_predicate import process_data
from querent.kg.ner_helperfunctions.contextual_embeddings import EntityEmbeddingExtractor
from querent.kg.ner_helperfunctions.graph_manager import KnowledgeGraphManager
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, List, Tuple
from querent.common.types.file_buffer import FileBuffer
from querent.logging.logger import setup_logger
from querent.kg.querent_kg import QuerentKG
from querent.graph.graph import QuerentGraph
from querent.config.graph_config import GraphConfig
from querent.kg.ner_helperfunctions.attn_scores import EntityAttentionExtractor
from querent.kg.ner_helperfunctions.filter_triples import TripleFilter
from querent.config.core.bert_llm_config import BERTLLMConfig




"""
    BERT-based Named Entity Recognition (NER) and Linking Language Model (LLM) for extracting entities and relationships from text.

    Inherits from:
        BaseEngine: Base class for processing engines.

    Attributes:
        graph_config (GraphConfig): Configuration for the graph.
        logger (Logger): Logger instance for logging errors and information.
        file_buffer (FileBuffer): Buffer for storing files.
        ner_tokenizer (AutoTokenizer): Tokenizer for the NER model.
        ner_model (Model): Pre-trained NER model.
        ner_llm_instance (NER_LLM): Instance of the NER_LLM class.
        attn_scores_instance (EntityAttentionExtractor): Instance for extracting attention scores.
        entity_embedding_extractor (EntityEmbeddingExtractor, optional): Instance for extracting entity embeddings.
        triple_filter_instance (EntityTripleFilter

    Methods:
        validate() -> bool:
            Validates if the NER model and tokenizer are initialized.

        process_messages(data: IngestedMessages):
            Processes the ingested messages.

        process_code(data: IngestedCode):
            Processes the ingested code.

        validate_ingested_tokens(data: IngestedTokens) -> bool:
            Validates the ingested tokens.

        process_tokens(data: IngestedTokens):
            Processes the ingested tokens, extracts entities, and builds the knowledge graph.
    """


class BERTLLM(BaseEngine):
    def __init__(
        self,
        input_queue:QuerentQueue,
        config: BERTLLMConfig
    ):  
        self.logger = setup_logger(config.logger, "BERTLLM")
        super().__init__(input_queue)
        self.graph_config = GraphConfig(identifier=config.ner_model_name)
        self.contextual_graph = QuerentKG(self.graph_config)
        self.semantic_graph = QuerentKG(self.graph_config)
        self.file_buffer = FileBuffer()
        self.ner_tokenizer = AutoTokenizer.from_pretrained(config.ner_model_name)
        self.ner_model = NER_LLM.load_model(config.ner_model_name, "NER")
        self.ner_llm_instance = NER_LLM(
            provided_tokenizer=self.ner_tokenizer, provided_model=self.ner_model
        )
        self.attn_scores_instance = EntityAttentionExtractor(model=self.ner_model, tokenizer=self.ner_tokenizer)
        self.enable_filtering = config.enable_filtering
        self.filter_params = config.filter_params or {}
        self.triple_filter = None
        if self.enable_filtering:
            self.triple_filter = TripleFilter(**self.filter_params)
 

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    async def process_code(self, data: IngestedCode):
        return super().process_messages(data)

    @staticmethod
    def validate_ingested_tokens(data: IngestedTokens) -> bool:
        if not data.data or data.is_error():
            
            return False

        return True

    def count_entity_pairs(self, doc_entity_pairs):
        total_pairs = 0
        for inner_list in doc_entity_pairs:
            total_pairs += len(inner_list)
            
        return total_pairs
    
    def set_filter_params(self, **kwargs):
        self.filter_params = kwargs
        if self.triple_filter:
            self.triple_filter.set_params(**kwargs)
        else:
            self.triple_filter = TripleFilter(**kwargs)

    async def process_tokens(self, data: IngestedTokens):
        doc_entity_pairs = []
        number_sentences = 0
        try:
            if data is None or data.is_error():
                self.set_termination_event()

                return

            filename, content = self.file_buffer.add_chunk(
                data.get_file_path(), data.data
            )
            if content:
                tokens = self.ner_llm_instance._tokenize_and_chunk(content)
                for tokenized_sentence, original_sentence, sentence_idx in tokens:
                    (
                        entities,
                        entity_pairs,
                    ) = self.ner_llm_instance.extract_entities_from_sentence(
                        original_sentence, sentence_idx, [s[1] for s in tokens]
                    )
                    doc_entity_pairs.append(
                        self.ner_llm_instance.transform_entity_pairs(entity_pairs)
                    )
                    number_sentences = number_sentences + 1


            else:
                if not BERTLLM.validate_ingested_tokens(data):
                    self.set_termination_event()
            if doc_entity_pairs:
                pairs_withattn = self.attn_scores_instance.extract_and_append_attention_weights(doc_entity_pairs)
                if self.count_entity_pairs(pairs_withattn)>1:
                    self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer, self.count_entity_pairs(pairs_withattn), number_sentences=number_sentences)
                else :
                    self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer, 2, number_sentences=number_sentences)
                pairs_withemb = self.entity_embedding_extractor.extract_and_append_entity_embeddings(pairs_withattn)
                pairs_with_predicates = process_data(pairs_withemb, filename)
                if self.enable_filtering == True:
                    clustered_triples, cluster_reduction_count, clusterer = self.triple_filter.cluster_triples(pairs_with_predicates)
                    filtered_triples, reduction_count = self.triple_filter.filter_triples(clustered_triples)
                else:
                    filtered_triples = pairs_with_predicates
                kgm = KnowledgeGraphManager()
                kgm.feed_input(filtered_triples)
                current_state = EventState(EventType.TOKEN_PROCESSED, 1.0, kgm.retrieve_triples())
                await self.set_state(new_state=current_state)
        except Exception as e:
            self.logger.error(
                f"Invalid {self.__class__.__name__} configuration. Unable to process tokens. {e}"
            )
            raise Exception(
                f"An unexpected error occurred while processing tokens: {e}"
            )
