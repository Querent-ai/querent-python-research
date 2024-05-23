from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import SearchContextualRelationship as sc
from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import EntityPair as ep
from querent.kg.rel_helperfunctions.attn_based_relationship_seach_scope import perform_search
from dataclasses import dataclass
from typing import Optional


@dataclass
class Entity:
    text: str


@dataclass
class SemanticPairs:
    head: Entity
    tail: Entity
    relations: list[str]


class IndividualFilter:
    def __init__(self, forward_relations: bool, threshold: float, token_idx_with_word: list, spacy_doc):
        self.forward_relations = forward_relations
        self.threshold = threshold
        self.token_idx_with_word = token_idx_with_word
        self.doc = spacy_doc

    def filter(self, candidates: list[sc], e_pair: ep) -> SemanticPairs:
        print("---------------", e_pair)
        response = SemanticPairs(
            head=Entity(
                text=e_pair.head_entity['noun_chunk'].lower()
            ),
            tail=Entity(
                text=e_pair.tail_entity['noun_chunk'].lower()
            ),
            relations=[]
        )

        for candidate in candidates:
            print("-----------Relation Token ", candidate.relation_tokens)
            print("-----------Relation Score ", candidate.mean_score())
            if candidate.mean_score() < self.threshold:
                print("Less Scorte")
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
        return response

    def lemmatize(self, relation: str, indexes: list[int]) -> str:
        if relation.isnumeric():
            return ''

        new_text = ''
        # Another option would be including 'AUX'
        remove_morpho = {'SYM', 'OTHER', 'PUNCT', 'NUM', 'INTJ'}
        last_word = ' '
        print("Relationshippppppppppp--------", relation)
        print("Indexxxxxxxxxx", indexes)
        words = []
        for idx in indexes:
            words.append(self.token_idx_with_word[idx -1])
        print("Wordssssssss", words)
        for word, word_id in words:
            token = next((token for token in self.doc if token.text.lower() == word), None)
            print("Tokennnnnnnnnnnnnnnnn", token, token.pos_)
            if token and token.pos_ not in remove_morpho:
                print("Finalyy adding -------------")
                new_word = token.lemma_.lower()
                if last_word != new_word:
                    print("Finalyy adding -------------")
                    new_text += new_word
                    new_text += ' '
                    last_word = new_word

        new_text = new_text.strip()
        return new_text

def clean_relations(ht_pairs: list[SemanticPairs]) -> list[SemanticPairs]:
    unique_relations = set()
    for ht_pair in ht_pairs:
        filtered_relations = []
        for relation in ht_pair.relations:
            unique_key = ht_pair.head.text + "|" + relation + "|" + ht_pair.tail.text
            reverse_key = ht_pair.tail.text + "|" + relation + "|" + ht_pair.head.text
            if unique_key not in unique_relations and reverse_key not in unique_relations:
                filtered_relations.append(relation)
                unique_relations.add(unique_key)
        ht_pair.relations = filtered_relations

    new_list = [pair for pair in ht_pairs if len(pair.relations) > 0 and
                (pair.head.text != pair.tail.text)]

    return new_list

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
context = {
    'current_sentence': 'Dr. Emily Stanton, a prominent figure in the Environmental Sciences Department, has been advocating for cleaner energy use on campus for years.',
    'previous_sentence': "This decision was influenced heavily by the growing concern among the student body and faculty about the city's escalating pollution levels.",
    'next_sentence': 'Her relentless efforts finally paid off when the university committed to a 40% reduction in carbon emissions over the next five years.'
}

tail_entity = {
    'entity': 'introduction gas injection',
    'label': 'geo-method',
    'score': 1.0,
    'noun_chunk': 'introduction gas injection',
}

head_entity = {
    'entity': 'oil production',
    'label': 'geo-method',
    'score': 1.0,
    'noun_chunk': 'oil production',
}

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


import transformers
from querent.kg.ner_helperfunctions.ner_llm_transformer import NER_LLM
from querent.kg.rel_helperfunctions.attn_based_relationship_model_getter import get_model
import numpy


tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased',from_tf=True )
model = transformers.BertModel.from_pretrained('bert-base-uncased', from_tf=True)

##Get end indexes of noun chunks

# combined_text = f"{context['previous_sentence']} {context['current_sentence']} {context['next_sentence']}"
# combined_text = "Dr. Emily Stanton, a prominent figure in the Environmental Sciences Department, has been advocating for cleaner energy use on campus for years."
# combined_text = "1. introduction gas injection has been a widely used technology for increasing oil production in unconventional shale plays in the united states, and it may be the most efficient approach for unlocking the remaining oil percentage. unconventional resources, like shale reservoirs, are widely recognized for their extremely low permeability and porosity.1 despite the fact that multistage hydraulic fracturing and horizontal well drilling techniques are used to extract the remaining oil from such reservoirs, only 4- 6% of the trapped oil can be extracted, and the oil production drops after a few months, attributing to the ultralow permeability.2-19 water injection is also one of the suitable strategies for increasing oil recovery from conventional reservoirs; nevertheless, due to weak injectivity, insuicient sweep potency, and clay swelling concerns, this approach is not the ideal solution for tight reservoirs.20,21 cyclic gas injection outperforms gas looding methods in terms of enhancing oil recovery, mainly in ultratight reservoirs.22,23 the total organic carbon (toc) is the most important inluencing parameter on gas injection in tight reservoirs because kerogen makes the surface of the pore oil-wet, making the oil inside challenging to extract.24 due to the combination of multiphase luids (i.e., gas, oil, condensate, and water) and scales, multiphase low production can create a number of challenges including wax and asphaltene deposition, hydrate formation, slugging, and emulsions.25 organic hydrocarbon particles settling in oil and gas reservoirs might create many low assurance problems throughout the extraction process."
combined_text = "1. introduction gas injection has been a widely used technology for increasing oil production in unconventional shale plays in the united states, and it may be the most efficient approach for unlocking the remaining oil percentage."
ner_helper = NER_LLM(ner_model_name="dummy",provided_model="dummy", provided_tokenizer= tokenizer)

head_positions = ner_helper.find_subword_indices(combined_text, head_entity['noun_chunk'])
tail_positions = ner_helper.find_subword_indices(combined_text, tail_entity['noun_chunk'])



##Initialize Entity Pair

entity_pair = ep(head_entity, tail_entity, context, head_positions, tail_positions)


# # Compute Attention_matrix 

extractor = get_model("bert",model_tokenizer= tokenizer,model=model)
tokenized_sentence = extractor.tokenize_sentence(combined_text)
model_input = extractor.model_input(tokenized_sentence)
attention_matrix = extractor.inference_attention(model_input)

print("Attention------- Done", numpy.shape(attention_matrix))




candidate_paths = perform_search(attention_matrix, entity_pair, search_candidates=5, require_contiguous=True, max_relation_length=8, num_initial_tokens=1)

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

candidate_paths = remove_duplicates(candidate_paths)


# Display candidate paths
for path in candidate_paths:
    print(f"Path: {path.relation_tokens}, Mean Score: {path.mean_score()}")

token_idx_with_word = ner_helper.tokenize_sentence_with_positions(combined_text)
print("Token_idx_wi&&&&&&&&&&&&&&&&", token_idx_with_word)
nlp_model = NER_LLM.set_nlp_model('en_core_web_lg')
nlp_model = NER_LLM.get_class_variable()
nlp = nlp_model
spacy_doc  = nlp(combined_text)
for index, token in enumerate(tokenizer.tokenize(combined_text)):

    print(f"Index {index}: {token}")
filter = IndividualFilter(True, 0.02, token_idx_with_word, spacy_doc)
filtered_results = filter.filter(candidates=candidate_paths,e_pair=entity_pair)
print("Final Results --------------", filtered_results)
print(head_positions, tail_positions)

print("Cleaned Relationships ------------", clean_relations([filtered_results]))

# for token in spacy_doc:
#     print("Token and Token Pos", token, "---------", token.pos_)