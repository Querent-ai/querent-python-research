from transformers import AutoTokenizer
from querent.kg.ner_helperfunctions.fixed_predicate import FixedPredicateExtractor
from querent.common.types.ingested_images import IngestedImages
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.kg.contextual_predicate import process_data
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
from querent.config.core.bert_llm_config import BERTLLMConfig
from querent.kg.rel_helperfunctions.triple_to_json import TripleToJsonConverter

class BERTLLM(BaseEngine):
    def __init__(
        self,
        input_queue:QuerentQueue,
        config: BERTLLMConfig
    ):  
        self.logger = setup_logger(__name__, "BERTLLM")
        super().__init__(input_queue)
        self.graph_config = GraphConfig(identifier=config.name)
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
        self.sample_entities = config.sample_entities
        self.fixed_entities = config.fixed_entities
        if self.fixed_entities and not self.sample_entities:
            raise ValueError("If specific entities are provided, their types should also be provided.")
        if self.fixed_entities and self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(fixed_entities=self.fixed_entities, entity_types=self.sample_entities)
        elif self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(entity_types=self.sample_entities)
        else:
            self.entity_context_extractor = None
        self.fixed_relationships = config.fixed_relationships
        self.sample_relationships = config.sample_relationships
        if self.fixed_relationships and not self.sample_relationships:
            raise ValueError("If specific predicates are provided, their types should also be provided.")
        if self.fixed_relationships and self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(fixed_predicates=self.fixed_relationships, predicate_types=self.sample_relationships)
        elif self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(predicate_types=self.sample_relationships)
        else:
            self.predicate_context_extractor = None
        self.user_context = config.user_context
 

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    
    def process_images(self, data: IngestedImages):
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

            file, content = self.file_buffer.add_chunk(
                data.get_file_path(), data.data
            )
            print("--------------------------------", content)
            if content:
                if self.fixed_entities:
                    content = self.entity_context_extractor.find_entity_sentences(content)
                    print("--------------------------------", content)
                if self.fixed_relationships:
                    content = self.predicate_context_extractor.find_predicate_sentences(content)
                    print("--------------------------------", content)
                tokens = self.ner_llm_instance._tokenize_and_chunk(content)
                print("tokens: ", tokens)
                for tokenized_sentence, original_sentence, sentence_idx in tokens:
                    (entities, entity_pairs,) = self.ner_llm_instance.extract_entities_from_sentence(original_sentence, sentence_idx, [s[1] for s in tokens],False, [''])
                    print("entity pairs", entity_pairs)
                    if entity_pairs:
                        doc_entity_pairs.append(self.ner_llm_instance.transform_entity_pairs(entity_pairs))
                    number_sentences = number_sentences + 1
            else:
                if not BERTLLM.validate_ingested_tokens(data):
                    self.set_termination_event()
            print("doc entities-----------------------", doc_entity_pairs)
            if self.sample_entities:
                doc_entity_pairs = self.entity_context_extractor.process_entity_types(doc_entities=doc_entity_pairs)
            print("doc entities---------------------", doc_entity_pairs)
            if doc_entity_pairs:
                pairs_withattn = self.attn_scores_instance.extract_and_append_attention_weights(doc_entity_pairs)
                print("-----------",pairs_withattn)
                if self.count_entity_pairs(pairs_withattn)>1:
                    self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer, self.count_entity_pairs(pairs_withattn), number_sentences=number_sentences)
                else :
                    self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer, 2, number_sentences=number_sentences)
                pairs_withemb = self.entity_embedding_extractor.extract_and_append_entity_embeddings(pairs_withattn)
                print("-----------",pairs_withemb)
                pairs_with_predicates = process_data(pairs_withemb, file)
                if self.enable_filtering == True and not self.entity_context_extractor:
                    cluster_output = self.triple_filter.cluster_triples(pairs_with_predicates)
                    clustered_triples = cluster_output['filtered_triples']
                    cluster_labels = cluster_output['cluster_labels']
                    cluster_persistence = cluster_output['cluster_persistence']
                    final_clustered_triples = self.triple_filter.filter_by_cluster_persistence(pairs_with_predicates, cluster_persistence, cluster_labels)
                    if final_clustered_triples is not None:
                        filtered_triples, _ = self.triple_filter.filter_triples(final_clustered_triples)
                    else:
                        filtered_triples, _ = self.triple_filter.filter_triples(clustered_triples)
                        self.logger.log(f"Filtering in {self.__class__.__name__} producing 0 entity pairs. Filtering Disabled. ")
                else:
                    filtered_triples = pairs_with_predicates   
                mock_config = RelationshipExtractorConfig()
                semantic_extractor = RelationExtractor(mock_config)
                relationships = semantic_extractor.process_tokens(filtered_triples)
                embedding_triples = semantic_extractor.generate_embeddings(relationships)
                print("-------------------------------- embedding triples: {}".format(embedding_triples))
                if self.sample_relationships:
                    embedding_triples = self.predicate_context_extractor.process_predicate_types(embedding_triples)
                for triple in embedding_triples:
                    graph_json = TripleToJsonConverter.convert_graphjson(triple)
                    print("-------------------------------- Graph : {}".format(graph_json))
                    if graph_json:
                        current_state = EventState(EventType.Graph,1.0, graph_json, file)
                        await self.set_state(new_state=current_state)
                    vector_json = TripleToJsonConverter.convert_vectorjson(triple)
                    if vector_json:
                        current_state = EventState(EventType.Vector,1.0, vector_json, file)
                        await self.set_state(new_state=current_state)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Unable to process tokens. {e}")
            raise Exception(f"An unexpected error occurred while processing tokens: {e}")
