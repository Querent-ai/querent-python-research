import json
import spacy
from transformers import AutoTokenizer
from querent.kg.ner_helperfunctions.fixed_predicate import FixedPredicateExtractor
from querent.common.types.ingested_images import IngestedImages
from querent.config.core.opensource_llm_config import Opensource_LLM_Config
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.kg.rel_helperfunctions.contextual_predicate import process_data
from querent.kg.ner_helperfunctions.contextual_embeddings import EntityEmbeddingExtractor
from querent.kg.ner_helperfunctions.fixed_entities import FixedEntityExtractor
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
from querent.config.core.llm_config import LLM_Config
from querent.kg.rel_helperfunctions.triple_to_json import TripleToJsonConverter
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
import time

"""
    BERTLLM is a class derived from BaseEngine designed for processing language models, particularly focusing on named entity recognition and relationship extraction in text. It integrates various components for handling different types of input data (messages, images, code, tokens), extracting entities, filtering relevant information, and constructing knowledge graphs.

    Key functionalities include:
    - Initializing with a specific configuration for named entity recognition (NER) and language model processing.
    - Validating the presence of NER models and tokenizers.
    - Processing various types of input data like messages, images, code, and tokens.
    - Implementing methods for counting entity pairs, setting filter parameters, and processing tokens.
    - Extracting and clustering entities and relationships from the text, and converting them into graph and vector formats.
    - Handling errors and maintaining robustness in data processing.

    The class also incorporates mechanisms for filtering and clustering entities and relationships, as well as extracting embeddings and generating output in different formats.
    """


class BERTLLM(BaseEngine):
    def __init__(
        self,
        input_queue:QuerentQueue,
        config: LLM_Config
    ):  
        self.logger = setup_logger(__name__, "BERTLLM")
        super().__init__(input_queue)
        self.skip_inferences=config.skip_inferences
        if not self.skip_inferences:
            mock_config = Opensource_LLM_Config(qa_template=config.user_context,
                                                model_type = config.rel_model_type,
                                                model_path = config.rel_model_path,
                                                grammar_file_path = config.grammar_file_path,
                                                emb_model_name = config.emb_model_name)
            self.semantic_extractor = RelationExtractor(mock_config)
        self.graph_config = GraphConfig(identifier=config.name)
        self.contextual_graph = QuerentKG(self.graph_config)
        self.semantic_graph = QuerentKG(self.graph_config)
        self.file_buffer = FileBuffer()
        self.ner_tokenizer = AutoTokenizer.from_pretrained(config.ner_model_name)
        self.ner_model = NER_LLM.load_model(config.ner_model_name, "NER")
        self.ner_llm_instance = NER_LLM(provided_tokenizer=self.ner_tokenizer, provided_model=self.ner_model)
        self.nlp_model = NER_LLM.get_class_variable()
        self.create_emb = EmbeddingStore(inference_api_key=config.huggingface_token)
        self.attn_scores_instance = EntityAttentionExtractor(model=self.ner_model, tokenizer=self.ner_tokenizer)
        self.enable_filtering = config.enable_filtering
        self.filter_params = config.filter_params or {}
        self.triple_filter = None
        if self.enable_filtering:
            self.triple_filter = TripleFilter(**self.filter_params)
        self.sample_entities = config.sample_entities
        self.fixed_entities = config.fixed_entities
        if self.fixed_entities and not self.sample_entities:
            raise ValueError("If specific entities are provided, their types should also be provided.")
        if self.fixed_entities and self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(fixed_entities=self.fixed_entities, entity_types=self.sample_entities,model = self.nlp_model)
        elif self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(entity_types=self.sample_entities, model = self.nlp_model)
        else:
            self.entity_context_extractor = None
        self.fixed_relationships = config.fixed_relationships
        self.sample_relationships = config.sample_relationships
        if self.fixed_relationships and not self.sample_relationships:
            raise ValueError("If specific predicates are provided, their types should also be provided.")
        if self.fixed_relationships and self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(fixed_predicates=self.fixed_relationships, predicate_types=self.sample_relationships,model = self.nlp_model)
        elif self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(predicate_types=self.sample_relationships,model = self.nlp_model)
        else:
            self.predicate_context_extractor = None
        self.user_context = config.user_context
        self.isConfinedSearch = config.is_confined_search
        
 

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    
    def process_images(self, data: IngestedImages):
        return super().process_images(data)

    async def process_code(self, data: IngestedCode):
        return super().process_code(data)

    @staticmethod
    def validate_ingested_tokens(data: IngestedTokens) -> bool:
        if data.is_error():
            
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
            if not BERTLLM.validate_ingested_tokens(data):
                    self.set_termination_event()                                      
                    return
            if data.data:
                single_string = ' '.join(data.data)
                clean_text = single_string.replace('\n', ' ')
            else:
                clean_text = data.data
            if not data.is_token_stream : 
                file, content = self.file_buffer.add_chunk(
                data.get_file_path(), clean_text)
            else:
                content = clean_text
                file = data.get_file_path()
            if content:
                if self.fixed_entities:
                    content = self.entity_context_extractor.find_entity_sentences(content)
                if self.fixed_relationships:
                    content = self.predicate_context_extractor.find_predicate_sentences(content)
                tokens = self.ner_llm_instance._tokenize_and_chunk(content)
                for tokenized_sentence, original_sentence, sentence_idx in tokens:
                    (entities, entity_pairs,) = self.ner_llm_instance.extract_entities_from_sentence(original_sentence, sentence_idx, [s[1] for s in tokens],self.isConfinedSearch, self.fixed_entities, self.sample_entities)
                    if entity_pairs:
                        doc_entity_pairs.append(self.ner_llm_instance.transform_entity_pairs(entity_pairs))
                    number_sentences = number_sentences + 1
            else:
                return
            if self.sample_entities:
                doc_entity_pairs = self.entity_context_extractor.process_entity_types(doc_entities=doc_entity_pairs)
            if doc_entity_pairs and any(doc_entity_pairs):
                doc_entity_pairs = self.ner_llm_instance.remove_duplicates(doc_entity_pairs)
                pairs_withattn = self.attn_scores_instance.extract_and_append_attention_weights(doc_entity_pairs)
                if self.enable_filtering == True and not self.entity_context_extractor and self.count_entity_pairs(pairs_withattn)>1 and not self.predicate_context_extractor:
                    self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer)
                    pairs_withemb = self.entity_embedding_extractor.extract_and_append_entity_embeddings(pairs_withattn)
                else:
                    pairs_withemb = pairs_withattn
                pairs_with_predicates = process_data(pairs_withemb, file)
                if self.enable_filtering == True and not self.entity_context_extractor and self.count_entity_pairs(pairs_withattn)>1 and not self.predicate_context_extractor:
                    cluster_output = self.triple_filter.cluster_triples(pairs_with_predicates)
                    clustered_triples = cluster_output['filtered_triples']
                    cluster_labels = cluster_output['cluster_labels']
                    cluster_persistence = cluster_output['cluster_persistence']
                    final_clustered_triples = self.triple_filter.filter_by_cluster_persistence(pairs_with_predicates, cluster_persistence, cluster_labels)
                    if final_clustered_triples:
                        filtered_triples, reduction_count = self.triple_filter.filter_triples(final_clustered_triples)
                    else:
                        filtered_triples, _ = self.triple_filter.filter_triples(clustered_triples)
                        self.logger.error(f"Filtering in {self.__class__.__name__} producing 0 entity pairs. Filtering Disabled. ")
                else:
                    filtered_triples = pairs_with_predicates
                if not filtered_triples:
                    raise Exception("No entity pairs")
                if not self.skip_inferences:
                    relationships = self.semantic_extractor.process_tokens(filtered_triples[:2])
                    if len(relationships) > 0:
                        embedding_triples = self.create_emb.generate_embeddings(relationships)
                        if self.sample_relationships:
                            embedding_triples = self.predicate_context_extractor.process_predicate_types(embedding_triples)
                        for triple in embedding_triples:
                            graph_json = json.dumps(TripleToJsonConverter.convert_graphjson(triple))
                            if graph_json:
                                current_state = EventState(EventType.Graph,1.0, graph_json, file)
                                await self.set_state(new_state=current_state)
                            vector_json = json.dumps(TripleToJsonConverter.convert_vectorjson(triple))
                            if vector_json:
                                current_state = EventState(EventType.Vector,1.0, vector_json, file)
                                await self.set_state(new_state=current_state)
                    else:
                        return
                else:
                    return filtered_triples, file
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to process tokens. {e}")
            raise Exception(f"An unexpected error occurred while processing tokens: {e}")
