import ast
import json
import torch
from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import SearchContextualRelationship as sc
from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import EntityPair as ep
from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import perform_search
from dataclasses import dataclass
from querent.logging.logger import setup_logger
from typing import Optional
from collections import defaultdict
import numpy
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM

@dataclass
class Entity:
    text: str


@dataclass
class SemanticPairs:
    head: Entity
    tail: Entity
    relations: list[str]
    scores: list[float]


class IndividualFilter:
    def __init__(self, forward_relations: bool, threshold: float, token_idx_with_word: list, spacy_doc):
        self.forward_relations = forward_relations
        self.threshold = threshold
        self.token_idx_with_word = token_idx_with_word
        self.doc = spacy_doc

    def filter(self, candidates: list[sc], e_pair: ep) -> SemanticPairs:
        response = SemanticPairs(
            head=Entity(
                text=e_pair.head_entity['noun_chunk'].lower()
            ),
            tail=Entity(
                text=e_pair.tail_entity['noun_chunk'].lower()
            ),
            relations=[], 
            scores = [0]
        )
        counter = 0
        for candidate in candidates:
            if candidate.mean_score() < self.threshold:
                continue
            rel_txt = ''
            rel_idx = []
            last_index = None
            valid = True
            
            for token_id in candidate.relation_tokens:
                word, word_id = self.token_idx_with_word[token_id -1]
                if self.forward_relations and last_index is not None and word_id - last_index != 1:
                    valid = False
                    break
                last_index = word_id

                if len(rel_txt) > 0:
                    rel_txt += ' '
                lowered_word = word.lower()
                if lowered_word not in e_pair.head_entity['noun_chunk'] and lowered_word not in e_pair.tail_entity['noun_chunk']:
                    rel_txt += word.lower()
                    rel_idx.append(word_id)

            if valid:
                rel_txt = self.lemmatize(rel_txt, rel_idx)
                if len(rel_txt) == 0:
                    continue

                response.relations.append(rel_txt)
                response.scores.append(candidate.mean_score())
                counter = counter +1
        del response.scores[0]
        return response
    
    def combine_entities(self, entity_list):
        # This list will store the final entities after combining
        combined_entities = []
        # Temporary storage for current entity being processed
        current_entity = None

        for entity, index in entity_list:
            if entity.startswith('##'):
                # If the entity starts with ##, concatenate it with the last part of current_entity
                if current_entity:
                    current_entity = (current_entity[0] + entity[2:], current_entity[1])
            else:
                # If the current_entity is not None, it means we have completed processing an entity
                if current_entity:
                    combined_entities.append(current_entity)
                # Start a new entity
                current_entity = (entity, len(combined_entities) + 1)
        
        # Append the last processed entity if any
        if current_entity:
            combined_entities.append(current_entity)

        return combined_entities

    def lemmatize(self, relation: str, indexes: list[int]) -> str:
        if relation.isnumeric():
            return ''

        new_text = ''
        # Another option would be including 'AUX'
        remove_morpho = {'SYM', 'OTHER', 'PUNCT', 'NUM', 'INTJ', 'DET', 'ADP', 'PART'}
        last_word = ' '
        words = []
        for idx in indexes:
            words.append(self.token_idx_with_word[idx -1])
        words = self.combine_entities(words)
        for word, word_id in words:
            token = next((token for token in self.doc if word in token.text.lower()), None)
            if token and token.pos_ not in remove_morpho:
                new_word = token.lemma_.lower()
                if last_word != new_word:
                    new_text += new_word
                    new_text += ' '
                    last_word = new_word

        new_text = new_text.strip()
        return new_text

def get_best_relation(semantic_pair):
    scores = [score.item() if isinstance(score, torch.Tensor) else score for score in semantic_pair.scores]
    max_index = scores.index(max(scores))
    best_relation = semantic_pair.relations[max_index]
    best_score = scores[max_index]
    
    return best_relation, best_score


def frequency_cutoff(ht_relations: list[SemanticPairs], frequency: int):
    if frequency == 1:
        return
    counter: dict[str, int] = {}
    for ht_item in ht_relations:
        for relation in ht_item.relations:
            if relation in counter:
                counter[relation] += 1
            else:
                counter[relation] = 1

    for ht_item in ht_relations:
        ht_item.relations = [rel for rel in ht_item.relations if counter[rel] >= frequency]

def trim_triples(data):
    try:
        trimmed_data = []
        for entity1, predicate, entity2 in data:
            predicate_dict = json.loads(predicate)
            trimmed_predicate = {
                'context': predicate_dict.get('context', ''),
                'entity1_nn_chunk': predicate_dict.get('entity1_nn_chunk', ''),
                'entity2_nn_chunk': predicate_dict.get('entity2_nn_chunk', ''),
                'entity1_label': predicate_dict.get('entity1_label', ''),
                'entity2_label': predicate_dict.get('entity2_label', ''),
                'file_path': predicate_dict.get('file_path', ''),
                'current_sentence': predicate_dict.get('current_sentence', '')
            }
            trimmed_data.append((entity1, trimmed_predicate, entity2))

        return trimmed_data
    except Exception as e:
        raise Exception(f'Error in trimming triples: {e}')

def process_tokens(ner_instance : NER_LLM, extractor, filtered_triples, nlp_model):
    try:
        updated_triples = []
        for subject, predicate_metadata, object in filtered_triples:
            try:
                context = predicate_metadata['current_sentence'].replace("\n"," ")
                head_positions = ner_instance.find_subword_indices(context, predicate_metadata['entity1_nn_chunk'])
                tail_positions = ner_instance.find_subword_indices(context, predicate_metadata['entity2_nn_chunk'])
                if head_positions[0][0] > tail_positions[0][0]:
                    head_entity = {'entity': object, 'noun_chunk':predicate_metadata['entity2_nn_chunk'], 'entity_label':predicate_metadata['entity2_label'] }
                    tail_entity =  {'entity': subject, 'noun_chunk':predicate_metadata['entity1_nn_chunk'], 'entity_label':predicate_metadata['entity1_label']} 
                    entity_pair = ep(head_entity, tail_entity, context, tail_positions, head_positions)
                else:
                    head_entity = {'entity': subject, 'noun_chunk':predicate_metadata['entity1_nn_chunk'], 'entity_label':predicate_metadata['entity1_label']}
                    tail_entity =  {'entity': object, 'noun_chunk':predicate_metadata['entity2_nn_chunk'], 'entity_label':predicate_metadata['entity2_label']} 
                    entity_pair = ep(head_entity, tail_entity, context, head_positions, tail_positions)
                tokenized_sentence = extractor.tokenize_sentence(context)
                model_input = extractor.model_input(tokenized_sentence)
                attention_matrix = extractor.inference_attention(model_input)
                token_idx_with_word = ner_instance.tokenize_sentence_with_positions(context)
                spacy_doc  = nlp_model(context)
                filter = IndividualFilter(True, 0.02, token_idx_with_word, spacy_doc)
            
                ## HEAD Entity Based Attention Search
                candidate_paths = perform_search(entity_pair.head_entity['start_idx'], attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=extractor.num_start_tokens())
                candidate_paths = remove_duplicates(candidate_paths)
                filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
                predicate_he, score_he = get_best_relation(filtered_results)
                
                ##TAIL ENTITY Based Attention Search
                candidate_paths = perform_search(entity_pair.tail_entity['start_idx'], attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=extractor.num_start_tokens())
                candidate_paths = remove_duplicates(candidate_paths)
                filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
                predicate_te, score_te = get_best_relation(filtered_results)

                if score_he > score_te and (score_he >= 0.1 or score_te >= 0.1):
                    triple = create_semantic_triple(head_entity=head_entity['noun_chunk'],
                                                    tail_entity=tail_entity['noun_chunk'],
                                                    predicate=predicate_he,
                                                    score=score_he,
                                                    predicate_metadata=predicate_metadata,
                                                    subject_type=head_entity['entity_label'],
                                                    object_type=tail_entity['entity_label'])
                    updated_triples.append(triple)
                elif score_he < score_te and (score_he >= 0.1 or score_te >= 0.1):
                    triple = create_semantic_triple(head_entity=tail_entity['noun_chunk'],
                                                    tail_entity=head_entity['noun_chunk'],
                                                    predicate=predicate_te,
                                                    score=score_te,
                                                    predicate_metadata=predicate_metadata,
                                                    subject_type=tail_entity['entity_label'],
                                                    object_type=head_entity['entity_label'])
                    updated_triples.append(triple)
            except Exception as e:
                continue 
        return updated_triples
    except Exception as e:
        raise Exception(f'Error in extracting Attention Based Relationships: {e}')


def remove_duplicates(candidate_paths):
    seen_relations = set()
    unique_paths = []

    for path in candidate_paths:
        # Convert the relation_tokens to a tuple to make it hashable
        relation_tokens_tuple = tuple(path.relation_tokens)
        if relation_tokens_tuple not in seen_relations:
            seen_relations.add(relation_tokens_tuple)
            unique_paths.append(path)

    return unique_paths

def create_semantic_triple(head_entity, tail_entity, predicate, score, predicate_metadata, subject_type, object_type):
        try:   
            triple = (
                head_entity,
                json.dumps({
                    "predicate": predicate,
                    "predicate_type": "",
                    "context": predicate_metadata["context"].replace('\n',' '),
                    "file_path": predicate_metadata["file_path"],
                    "subject_type": subject_type,
                    "object_type": object_type,
                    "score":score,
                }),
                tail_entity
            )
            return triple
        except Exception as e:
            raise Exception(f"Error in creating semantic triple: {e}")
