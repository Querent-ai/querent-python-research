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
                response.scores.append((response.scores[counter] + candidate.mean_score()))
                # print("Response---", response)
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
                print("This is the context---------", context)
                head_positions = ner_instance.find_subword_indices(context, predicate_metadata['entity1_nn_chunk'])
                tail_positions = ner_instance.find_subword_indices(context, predicate_metadata['entity2_nn_chunk'])
                print("Head and Tail positions acquired----", head_positions, tail_positions)
                if head_positions[0][0] > tail_positions[0][0]:
                    head_entity = {'entity': object, 'noun_chunk':predicate_metadata['entity2_nn_chunk'], 'entity_label':predicate_metadata['entity2_label'] }
                    tail_entity =  {'entity': subject, 'noun_chunk':predicate_metadata['entity1_nn_chunk'], 'entity_label':predicate_metadata['entity1_label']} 
                    entity_pair = ep(head_entity, tail_entity, context, tail_positions, head_positions)
                else:
                    head_entity = {'entity': subject, 'noun_chunk':predicate_metadata['entity1_nn_chunk'], 'entity_label':predicate_metadata['entity1_label']}
                    tail_entity =  {'entity': object, 'noun_chunk':predicate_metadata['entity2_nn_chunk'], 'entity_label':predicate_metadata['entity2_label']} 
                    entity_pair = ep(head_entity, tail_entity, context, head_positions, tail_positions)
                print("Entity Pair---------", ep)
                tokenized_sentence = extractor.tokenize_sentence(context)
                model_input = extractor.model_input(tokenized_sentence)
                attention_matrix = extractor.inference_attention(model_input)
                token_idx_with_word = ner_instance.tokenize_sentence_with_positions(context)
                spacy_doc  = nlp_model(context)
                filter = IndividualFilter(True, 0.02, token_idx_with_word, spacy_doc)
            
                ## HEAD Entity Based Attention Search
                print("Lets start Perform Search")
                candidate_paths = perform_search(entity_pair.head_entity['start_idx'], attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=extractor.num_start_tokens())
                candidate_paths = remove_duplicates(candidate_paths)
                print("Search Finished------------")
                filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
                predicate_he, score_he = get_best_relation(filtered_results)
                print("Context----", context)
                print("------------", predicate_he,"-------------------", score_he)
                
                ##TAIL ENTITY Based Attention Search
                candidate_paths = perform_search(entity_pair.tail_entity['start_idx'], attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=extractor.num_start_tokens())
                candidate_paths = remove_duplicates(candidate_paths)
                filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
                predicate_te, score_te = get_best_relation(filtered_results)
                print("------------222222", predicate_te,"-------------------", score_te)

                if score_he > score_te and (score_he >= 0.2 or score_te >= 0.2):
                    triple = create_semantic_triple(head_entity=head_entity['noun_chunk'],
                                                    tail_entity=tail_entity['noun_chunk'],
                                                    predicate=predicate_he,
                                                    score=score_he,
                                                    predicate_metadata=predicate_metadata,
                                                    subject_type=head_entity['entity_label'],
                                                    object_type=tail_entity['entity_label'])
                    updated_triples.append(triple)
                elif score_he < score_te and (score_he >= 0.2 or score_te >= 0.2):
                    triple = create_semantic_triple(head_entity=tail_entity['noun_chunk'],
                                                    tail_entity=head_entity['noun_chunk'],
                                                    predicate=predicate_te,
                                                    score=score_te,
                                                    predicate_metadata=predicate_metadata,
                                                    subject_type=tail_entity['entity_label'],
                                                    object_type=head_entity['entity_label'])
                    updated_triples.append(triple)
            except Exception as e:
                print(f"Caught an exception: {e}")
                continue 
        return updated_triples
    except Exception as e:
        print("Exception in process tokens -----", e)
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
            print(f"Error in creating semantic triple: {e}")
            raise Exception(f"Error in creating semantic triple: {e}")

# Example usage
# head_entity = {
#     'entity': 'Emily',
#     'label': 'I-PER',
#     'score': 1.0,
#     'noun_chunk': 'Dr. Emily Stanton',
# }

# tail_entity = {
#     'entity': 'Environmental',
#     'label': 'I-ORG',
#     'score': 1.0,
#     'noun_chunk': 'Environmental Sciences Department',
# }
# context = {
#     'current_sentence': 'Dr. Emily Stanton, a prominent figure in the Environmental Sciences Department, has been advocating for cleaner energy use on campus for years.',
#     'previous_sentence': "This decision was influenced heavily by the growing concern among the student body and faculty about the city's escalating pollution levels.",
#     'next_sentence': 'Her relentless efforts finally paid off when the university committed to a 40% reduction in carbon emissions over the next five years.'
# }

# head_entity = {
#     'entity': 'gas injection',
#     'label': 'geo-method',
#     'score': 1.0,
#     'noun_chunk': 'gas injection',
# }

# tail_entity = {
#     'entity': 'oil production',
#     'label': 'geo-method',
#     'score': 1.0,
#     'noun_chunk': 'oil production',
# }

# head_entity = {
#     'entity': 'oil production',
#     'label': 'geo-method',
#     'score': 1.0,
#     'noun_chunk': 'oil production',
# }

# tail_entity = {
#     'entity': 'shale plays',
#     'label': 'geo-method',
#     'score': 1.0,
#     'noun_chunk': 'shale plays',
    
# }
# head_entity = {
#     'entity': 'nitrogen gas cyclic miscible and immiscible injection',
#     'label': 'organization',
#     'score': 1.0,
#     'noun_chunk': 'nitrogen gas cyclic miscible and immiscible injection',
# }

# tail_entity = {
#     'entity': 'oil recovery',
#     'label': 'group',
#     'score': 1.0,
#     'noun_chunk': 'oil recovery',
    
# }
# import transformers
# from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
# from querent.kg.rel_helperfunctions.attn_based_relationship_model_getter import get_model
# import numpy


# tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased',from_tf=True )
# model = transformers.BertModel.from_pretrained('bert-base-uncased', from_tf=True)

# tokenizer = transformers.BertTokenizer.from_pretrained("botryan96/GeoBERT",from_tf=True )
# model = transformers.BertModel.from_pretrained("botryan96/GeoBERT", from_tf=True)

##Get end indexes of noun chunks

# combined_text = f"{context['previous_sentence']} {context['current_sentence']} {context['next_sentence']}"
# combined_text = "Dr. Emily Stanton, a prominent figure in the Environmental Sciences Department, has been advocating for cleaner energy use on campus for years."
# combined_text = "1. introduction gas injection has been a widely used technology for increasing oil production in unconventional shale plays in the united states, and it may be the most efficient approach for unlocking the remaining oil percentage. unconventional resources, like shale reservoirs, are widely recognized for their extremely low permeability and porosity.1 despite the fact that multistage hydraulic fracturing and horizontal well drilling techniques are used to extract the remaining oil from such reservoirs, only 4- 6% of the trapped oil can be extracted, and the oil production drops after a few months, attributing to the ultralow permeability.2-19 water injection is also one of the suitable strategies for increasing oil recovery from conventional reservoirs; nevertheless, due to weak injectivity, insuicient sweep potency, and clay swelling concerns, this approach is not the ideal solution for tight reservoirs.20,21 cyclic gas injection outperforms gas looding methods in terms of enhancing oil recovery, mainly in ultratight reservoirs.22,23 the total organic carbon (toc) is the most important inluencing parameter on gas injection in tight reservoirs because kerogen makes the surface of the pore oil-wet, making the oil inside challenging to extract.24 due to the combination of multiphase luids (i.e., gas, oil, condensate, and water) and scales, multiphase low production can create a number of challenges including wax and asphaltene deposition, hydrate formation, slugging, and emulsions.25 organic hydrocarbon particles settling in oil and gas reservoirs might create many low assurance problems throughout the extraction process."
# combined_text = "1. introduction gas injection has been a widely used technology for increasing oil production in unconventional shale plays in the united states, and it may be the most efficient approach for unlocking the remaining oil percentage."
# combined_text = "asphaltene precipitation and deposition during nitrogen gas cyclic\nmiscible and immiscible injection in eagle ford shale and its impact\non oil recovery\nmukhtar elturki and abdulmohsin imqam*\n cite".replace("\n", " ")
# ner_helper = NER_LLM(ner_model_name="dummy",provided_model="dummy", provided_tokenizer= tokenizer)

# head_positions = ner_helper.find_subword_indices(combined_text, head_entity['noun_chunk'])
# tail_positions = ner_helper.find_subword_indices(combined_text, tail_entity['noun_chunk'])



# ##Initialize Entity Pair

# entity_pair = ep(head_entity, tail_entity, context, head_positions, tail_positions)


# # # Compute Attention_matrix 

# extractor = get_model("bert",model_tokenizer= tokenizer,model=model)
# tokenized_sentence = extractor.tokenize_sentence(combined_text)
# model_input = extractor.model_input(tokenized_sentence)
# attention_matrix = extractor.inference_attention(model_input)

# print("Attention------- Done", numpy.shape(attention_matrix))




# candidate_paths = perform_search(attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=1)



# candidate_paths = remove_duplicates(candidate_paths)


# # Display candidate paths
# for path in candidate_paths:
#     print(f"Path: {path.relation_tokens}, Mean Score: {path.mean_score()}")

# token_idx_with_word = ner_helper.tokenize_sentence_with_positions(combined_text)
# print("Token_idx_wi&&&&&&&&&&&&&&&&", token_idx_with_word)
# nlp_model = NER_LLM.set_nlp_model('en_core_web_lg')
# nlp_model = NER_LLM.get_class_variable()
# nlp = nlp_model
# spacy_doc  = nlp(combined_text)
# for index, token in enumerate(tokenizer.tokenize(combined_text)):

#     print(f"Index {index}: {token}")
# filter = IndividualFilter(True, 0.02, token_idx_with_word, spacy_doc)
# filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
# print("Final Results --------------", filtered_results)
# print(head_positions, tail_positions)

# # print("Cleaned Relationships ------------", clean_relations([filtered_results]))

# predicate, score = get_best_relation(filtered_results)
# print("------------", predicate,"-------------------", score)
# # for token in spacy_doc:
# #     print("Token and Token Pos", token, "---------", token.pos_)