import json
from transformers import AutoConfig, AutoTokenizer
import transformers
import time
from querent.common.types.ingested_table import IngestedTables
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
from querent.common.types.file_buffer import FileBuffer
from querent.logging.logger import setup_logger
from querent.kg.querent_kg import QuerentKG
from querent.config.graph_config import GraphConfig
from querent.kg.ner_helperfunctions.attn_scores import EntityAttentionExtractor
from querent.kg.ner_helperfunctions.filter_triples import TripleFilter
from querent.config.core.llm_config import LLM_Config
from querent.kg.rel_helperfunctions.triple_to_json import TripleToJsonConverter
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.models.model_manager import ModelManager
from querent.models.gguf_metadata_extractor import GGUFMetadataExtractor
from querent.kg.rel_helperfunctions.attn_based_relationship_model_getter import get_model
from querent.kg.rel_helperfunctions.attn_based_relationship_filter import process_tokens, trim_triples

class BERTLLM(BaseEngine):
    def __init__(
        self,
        input_queue: QuerentQueue,
        config: LLM_Config,
        Embedding=None
    ):
        self.logger = setup_logger(__name__, "BERTLLM")
        super().__init__(input_queue)
        self.skip_inferences = config.skip_inferences
        self.enable_filtering = config.enable_filtering
        self.filter_params = config.filter_params or {}
        self.sample_entities = config.sample_entities
        self.fixed_entities = config.fixed_entities
        self.fixed_relationships = config.fixed_relationships
        self.sample_relationships = config.sample_relationships
        self.user_context = config.user_context
        self.isConfinedSearch = config.is_confined_search
        self.attn_based_rel_extraction = True
        self.create_emb = EmbeddingStore() if not Embedding else Embedding

        try:
            self._initialize_components(config)
            self._initialize_models(config)
            self._initialize_extractors(config)
            self._initialize_entity_context_extractor()
            self._initialize_predicate_context_extractor(config)

            if self.enable_filtering:
                self.triple_filter = TripleFilter(**self.filter_params)
            else:
                self.triple_filter = None

        except Exception as e:
            self.logger.error("Error initializing BERT LLM Class")
            raise e

    def _initialize_components(self, config):
        self.graph_config = GraphConfig(identifier=config.name)
        self.contextual_graph = QuerentKG(self.graph_config)
        self.semantic_graph = QuerentKG(self.graph_config)
        self.file_buffer = FileBuffer()
        self.model_manager = ModelManager()

    def _initialize_models(self, config):
        self.ner_model_initialized = self.model_manager.get_model(config.ner_model_name)
        if not self.skip_inferences and self.attn_based_rel_extraction == False:
            extractor = GGUFMetadataExtractor(config.rel_model_path)
            model_metadata = extractor.dump_metadata()
            rel_model_name = extractor.extract_general_name(model_metadata)
            self.rel_model_initialized = self.model_manager.get_model(rel_model_name, model_path=config.rel_model_path)
        self.ner_llm_instance = NER_LLM(ner_model_name=self.ner_model_initialized)
        self.ner_tokenizer = self.ner_llm_instance.ner_tokenizer
        self.ner_model = self.ner_llm_instance.ner_model
        self.nlp_model = NER_LLM.set_nlp_model(config.spacy_model_path)
        self.nlp_model = NER_LLM.get_class_variable()

    def _initialize_extractors(self, config):
        if not self.skip_inferences and self.attn_based_rel_extraction == False:
            mock_config = Opensource_LLM_Config(
                qa_template=config.user_context,
                model_type=config.rel_model_type,
                model_path=self.rel_model_initialized,
                grammar_file_path=config.grammar_file_path,
                emb_model_name=config.emb_model_name,
                spacy_model_path=config.spacy_model_path,
                nltk_path=config.nltk_path
            )
            self.semantic_extractor = RelationExtractor(mock_config, self.create_emb)
            
        elif not self.skip_inferences and self.attn_based_rel_extraction == True:
            # config.rel_model_path = 'bert-base-uncased'
            config.rel_model_path = self.ner_model_initialized
            model_config = AutoConfig.from_pretrained(config.rel_model_path)
            if 'bert' in model_config.model_type.lower():
                self.ner_helper_instance = NER_LLM(ner_model_name=config.rel_model_path)
                self.ner_helper_tokenizer = self.ner_helper_instance.ner_tokenizer
                self.ner_helper_model = self.ner_helper_instance.ner_model
                self.extractor = get_model("bert",model_tokenizer= self.ner_helper_tokenizer,model=self.ner_helper_model)
            elif 'llama' in model_config.model_type.lower() or 'mpt' in model_config.model_type.lower():
                # model_id = "TheBloke/Llama-2-7B-GGUF"
                # filename = "llama-2-7b.Q5_K_M.gguf"
                # self.ner_tokenizer = AutoTokenizer.from_pretrained(model_id, gguf_file=filename)
                # self.model = transformers.AutoModelForCausalLM.from_pretrained(model_id, gguf_file=filename)
                # self.ner_helper_instance = NER_LLM(provided_tokenizer =self.ner_tokenizer, provided_model=self.model)
                self.model = transformers.AutoModelForCausalLM.from_pretrained(config.rel_model_path,trust_remote_code=True)
                # self.ner_helper_instance = NER_LLM(ner_model_name= config.rel_model_path, provided_model=self.model)
                self.ner_helper_instance = self.ner_llm_instance
                self.ner_helper_tokenizer = self.ner_helper_instance.ner_tokenizer
                self.ner_helper_model = self.ner_helper_instance.ner_model
                self.extractor = get_model("llama",model_tokenizer= self.ner_helper_tokenizer,model=self.ner_helper_model)
            else:
                raise ValueError("Selected Model not supported for Attnetion Based Graph Extraction")
        self.attn_scores_instance = EntityAttentionExtractor(model=self.ner_model, tokenizer=self.ner_tokenizer)

    def _initialize_entity_context_extractor(self):
        if self.fixed_entities and not self.sample_entities:
            raise ValueError("If specific entities are provided, their types should also be provided.")
        
        if self.fixed_entities and self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(
                fixed_entities=self.fixed_entities, 
                entity_types=self.sample_entities, 
                model=self.nlp_model
            )
        elif self.sample_entities:
            self.entity_context_extractor = FixedEntityExtractor(
                entity_types=self.sample_entities, 
                model=self.nlp_model
            )
        else:
            self.entity_context_extractor = None

    def _initialize_predicate_context_extractor(self, config):
        if self.fixed_relationships and not self.sample_relationships:
            raise ValueError("If specific predicates are provided, their types should also be provided.")
        
        self.predicate_json = None
        if self.skip_inferences:
            self.predicate_context_extractor = None
        elif self.fixed_relationships and self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(
                fixed_predicates=self.fixed_relationships, 
                predicate_types=self.sample_relationships, 
                model=self.nlp_model
            )
            self.predicate_json = self.predicate_context_extractor.construct_predicate_json(
                self.fixed_relationships, 
                self.sample_relationships
            )
        elif self.sample_relationships:
            self.predicate_context_extractor = FixedPredicateExtractor(
                predicate_types=self.sample_relationships, 
                model=self.nlp_model
            )
            self.predicate_json = self.predicate_context_extractor.construct_predicate_json(
                relationship_types=self.sample_relationships
            )
        else:
            self.predicate_context_extractor = None

        if self.predicate_json:
            self.predicate_json_emb = self.create_emb.generate_relationship_embeddings(self.predicate_json)

        
 

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)
    
    @staticmethod
    def validate_ingested_images(data: IngestedImages) -> bool:
        if data.is_error():
            
            return False

        return True
    async def process_images(self, data: IngestedImages):
        content = ""
        doc_entity_pairs = []
        doc_entity_pairs_ocr = []
        entity_ocr = []
        results = []
        blob = data.image
        try:
            doc_source = data.doc_source
            if not BERTLLM.validate_ingested_images(data):
                self.set_termination_event()                                      
                return
            if data.ocr_text:
                ocr_text = ' '.join(data.ocr_text)
            if data.text:
                content = ' '.join(data.text)
            file = data.file
            ocr_content = ocr_text
            if ocr_content or content:
                (entity_ocr, doc_entity_pairs_ocr) = self.ner_llm_instance.get_entity_pairs(isConfinedSearch= self.isConfinedSearch, 
                                                                                                  content=ocr_content,
                                                                                                  fixed_entities=self.fixed_entities,
                                                                                                  sample_entities=self.sample_entities)
                if len(doc_entity_pairs_ocr) >= 1:
                    results = doc_entity_pairs_ocr
                elif len(doc_entity_pairs_ocr) == 0:
                    if content and len(entity_ocr) >=1:
                        if self.fixed_entities:
                            content = self.entity_context_extractor.find_entity_sentences(content)
                        (_, doc_entity_pairs) = self.ner_llm_instance.get_entity_pairs(isConfinedSearch= self.isConfinedSearch, 
                                                                                                  content=content,
                                                                                                  fixed_entities=self.fixed_entities,
                                                                                                  sample_entities=self.sample_entities)
                        if len(doc_entity_pairs) > 0 and len(entity_ocr) >=1:
                            results = [self.ner_llm_instance.filter_matching_entities(doc_entity_pairs, entity_ocr)]
                        elif len(doc_entity_pairs) > 0 and len(entity_ocr) == 0:
                            # results = doc_entity_pairs
                            pass
                    else:
                        return        
                if len(results) > 0:
                    doc_entity_pairs = self.ner_llm_instance.remove_duplicates(results)
                    filtered_triples = process_data(doc_entity_pairs, file)
                    if self.skip_inferences:
                        return filtered_triples, file, self.ner_llm_instance
                    else:
                        unique_id = str(hash(data.image))
                        for triple in filtered_triples:
                            if not self.termination_event.is_set():
                                updated_tuple = self.ner_llm_instance.final_ingested_images_tuples(triple, create_embeddings=self.create_emb)
                                graph_json = json.dumps(TripleToJsonConverter.convert_graphjson(updated_tuple))
                                if graph_json:
                                    current_state = EventState(event_type=EventType.Graph, timestamp=time.time(), payload=graph_json, file=file, doc_source=doc_source, image_id=unique_id)
                                    await self.set_state(new_state=current_state)
                                subject, json_str, object_ = updated_tuple
                                context = json.loads(json_str)
                                sen_emb = self.create_emb.get_embeddings([context['context']])[0]
                                sub_emb = self.create_emb.get_embeddings(subject)[0]
                                obj_emb = self.create_emb.get_embeddings(object_)[0]
                                predicate_score=1
                                final_emb = TripleToJsonConverter.dynamic_weighted_average_embeddings(
                                                                                                            [sub_emb, obj_emb, sen_emb],
                                                                                                            base_weights=[predicate_score, predicate_score, 3],
                                                                                                            normalize_weights=True  # Normalize weights to ensure they sum to 1
                                                                                                        )
                                vector_json = json.dumps(TripleToJsonConverter.convert_vectorjson(updated_tuple, blob, final_emb))
                                if vector_json:
                                    current_state = EventState(event_type=EventType.Vector, timestamp=time.time(), payload=vector_json, file=file, doc_source=doc_source, image_id=unique_id)
                                    await self.set_state(new_state=current_state)
            else:
                return        
        except Exception as e:
            self.logger.debug(f"Invalid {self.__class__.__name__} configuration. Unable to process tokens. {e}")
    
    async def process_tables(self, data: IngestedTables):
        return super().process_tables(data)

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
        try:
            doc_entity_pairs = []
            doc_source = data.doc_source

            if not BERTLLM.validate_ingested_tokens(data):
                self.set_termination_event()
                return

            content, file = self._prepare_content(data)
            if not content:
                return
            if self.fixed_entities:
                content = self.entity_context_extractor.find_entity_sentences(content)
            doc_entity_pairs = self._get_entity_pairs(content)
            if not doc_entity_pairs:
                return

            doc_entity_pairs = self._process_entity_types(doc_entity_pairs)
            if not self.entity_context_extractor and not self.predicate_context_extractor:
                pairs_withattn = self.attn_scores_instance.extract_and_append_attention_weights(doc_entity_pairs)
            else:
                pairs_withattn = doc_entity_pairs
            pairs_with_predicates = self._process_pairs_with_embeddings(pairs_withattn, file)
            filtered_triples = self._filter_triples(pairs_with_predicates, pairs_withattn)
            if not filtered_triples:
                return

            if not self.skip_inferences:
                await self._process_relationships(filtered_triples, file, doc_source)
            else:
                return filtered_triples, file

        except Exception as e:
            self.logger.debug(f"Invalid {self.__class__.__name__} configuration. Unable to process tokens. {e}")

    def _prepare_content(self, data):
        if data.data:
            clean_text = ' '.join(data.data)
        else:
            clean_text = data.data

        if not data.is_token_stream:
            file, content = self.file_buffer.add_chunk(data.get_file_path(), clean_text)
        else:
            content = clean_text
            file = data.get_file_path()
        return content, file

    def _get_entity_pairs(self, content):
        return self.ner_llm_instance.get_entity_pairs(
            isConfinedSearch=self.isConfinedSearch,
            content=content,
            fixed_entities=self.fixed_entities,
            sample_entities=self.sample_entities
        )[1]

    def _process_entity_types(self, doc_entity_pairs):
        if self.sample_entities:
            doc_entity_pairs = self.entity_context_extractor.process_entity_types(doc_entities=doc_entity_pairs)
        if any(doc_entity_pairs):
            doc_entity_pairs = self.ner_llm_instance.remove_duplicates(doc_entity_pairs)
        return doc_entity_pairs

    def _process_pairs_with_embeddings(self, pairs_withattn, file):
        if self.enable_filtering and not self.entity_context_extractor and self.count_entity_pairs(pairs_withattn) > 1 and not self.predicate_context_extractor:
            self.entity_embedding_extractor = EntityEmbeddingExtractor(self.ner_model, self.ner_tokenizer)
            pairs_withemb = self.entity_embedding_extractor.extract_and_append_entity_embeddings(pairs_withattn)
        else:
            pairs_withemb = pairs_withattn
        return process_data(pairs_withemb, file)

    def _filter_triples(self, pairs_with_predicates, pairs_withattn):
        if self.enable_filtering and not self.entity_context_extractor and self.count_entity_pairs(pairs_withattn) > 1 and not self.predicate_context_extractor:
            cluster_output = self.triple_filter.cluster_triples(pairs_with_predicates)
            clustered_triples = cluster_output['filtered_triples']
            if clustered_triples:
                filtered_triples, _ = self.triple_filter.filter_triples(clustered_triples)
            else:
                self.logger.debug(f"Filtering in {self.__class__.__name__} producing 0 entity pairs. Filtering Disabled.")
                filtered_triples = pairs_with_predicates
        else:
            filtered_triples = pairs_with_predicates
        return filtered_triples

    async def _process_relationships(self, filtered_triples, file, doc_source):
        if self.attn_based_rel_extraction == False:    
            relationships = self.semantic_extractor.process_tokens(
                filtered_triples, 
                fixed_entities=(len(self.sample_entities) >= 1)
            )
        else:
            filtered_triples = trim_triples(filtered_triples)
            relationships = process_tokens(filtered_triples=filtered_triples, ner_instance=self.ner_helper_instance, extractor=self.extractor, nlp_model=self.nlp_model)
        if not relationships:
            return

        embedding_triples = self._generate_embeddings(relationships)
        await self._process_embedding_triples(embedding_triples, file, doc_source)

    def _generate_embeddings(self, relationships):
        if self.fixed_relationships and self.sample_relationships:
            return self.create_emb.generate_embeddings(
                relationships, 
                relationship_finder=True, 
                generate_embeddings_with_fixed_relationship=True
            )
        elif self.sample_relationships:
            return self.create_emb.generate_embeddings(relationships, relationship_finder=True)
        else:
            return self.create_emb.generate_embeddings(relationships)

    async def _process_embedding_triples(self, embedding_triples, file, doc_source):
        if self.sample_relationships:
            embedding_triples = self.predicate_context_extractor.update_embedding_triples_with_similarity(
                self.predicate_json_emb, embedding_triples)

        for triple in embedding_triples:
            if self.termination_event.is_set():
                return

            graph_json = json.dumps(TripleToJsonConverter.convert_graphjson(triple))
            if graph_json:
                current_state = EventState(
                    event_type=EventType.Graph,
                    timestamp=time.time(),
                    payload=graph_json,
                    file=file,
                    doc_source=doc_source
                )
                await self.set_state(new_state=current_state)
            subject, json_str, object_ = triple
            context = json.loads(json_str)
            sen_emb = self.create_emb.get_embeddings([context['context']])[0]
            sub_emb = self.create_emb.get_embeddings(subject)[0]
            obj_emb = self.create_emb.get_embeddings(object_)[0]
            predicate_score=context['score']
            final_emb = TripleToJsonConverter.dynamic_weighted_average_embeddings(
                                                                                        [sub_emb, obj_emb, sen_emb],
                                                                                        base_weights=[predicate_score, predicate_score, 3],
                                                                                        normalize_weights=True  # Normalize weights to ensure they sum to 1
                                                                                    )
            vector_json = json.dumps(TripleToJsonConverter.convert_vectorjson(triple=triple, embeddings=final_emb))
            if vector_json:
                current_state = EventState(
                    event_type=EventType.Vector,
                    timestamp=time.time(),
                    payload=vector_json,
                    file=file,
                    doc_source=doc_source
                )
                await self.set_state(new_state=current_state)
