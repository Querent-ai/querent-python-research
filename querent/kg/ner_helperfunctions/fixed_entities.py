import spacy
import re
from typing import List

class FixedEntityExtractor:
    def __init__(self, fixed_entities: List[str] = None, entity_types: List[str] = None, model="en_core_web_lg"):
        self.nlp = spacy.load(model)
        self.entity_types = entity_types
        self.fixed_entities = fixed_entities

        if fixed_entities:
            self.entity_pattern = self.create_combined_pattern(fixed_entities)
            self.lemmatized_entities = set(self.lemmatize_entities(fixed_entities))


    def create_combined_pattern(self, entities):
        combined_pattern = '|'.join(map(re.escape, entities))
        return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)

    def lemmatize_entities(self, entities):
        return [self.nlp(entity)[0].lemma_ for entity in entities]

    def find_entity_sentences(self, text: str, chunk_size=1000) -> str:
        doc = self.nlp(text)

        relevant_sentences = []
        added_sentences = set()
        prev_sentence = None
        for j, sentence in enumerate(doc.sents):
            if self.is_entity_present(sentence):
                self.add_contextual_sentences(list(doc.sents), j, prev_sentence, relevant_sentences, added_sentences)

            prev_sentence = sentence

        return ' '.join(relevant_sentences)

    def is_entity_present(self, sentence):
        sentence_text = sentence.text
        sentence_lemmas = {token.lemma_ for token in sentence}
        return self.fixed_entities and (self.entity_pattern.search(sentence_text) or sentence_lemmas.intersection(self.lemmatized_entities))

    def add_contextual_sentences(self, sentences, current_index, prev_sentence, relevant_sentences, added_sentences):
        if prev_sentence and prev_sentence.text not in added_sentences:
            relevant_sentences.append(prev_sentence.text)
            added_sentences.add(prev_sentence.text)

        current_sentence = sentences[current_index]
        if current_sentence.text not in added_sentences:
            relevant_sentences.append(current_sentence.text)
            added_sentences.add(current_sentence.text)

        if current_index < len(sentences) - 1:
            next_sentence = sentences[current_index + 1]
            if next_sentence.text not in added_sentences:
                relevant_sentences.append(next_sentence.text)
                added_sentences.add(next_sentence.text)

    def measure_reduction(self, original_text: str, reduced_text: str) -> float:
        original_length = len(original_text)
        reduced_length = len(reduced_text)
        reduction_percentage = ((original_length - reduced_length) / original_length) * 100
        return reduction_percentage

    def process_entity_types(self, doc_entities):
        filtered_entities = []
        for entity_group in doc_entities:
            for entity_data in entity_group: 
                entity1, sentence, entity2, entity_info = entity_data
                entity1_labels = entity_info['entity1_label'].split(', ')
                entity2_labels = entity_info['entity2_label'].split(', ')
                entity1_nn_chunk = entity_info['entity1_nn_chunk']
                entity2_nn_chunk = entity_info['entity2_nn_chunk']

                if self.fixed_entities:
                    entity1_match = any(entity in entity1_nn_chunk for entity in self.fixed_entities) and any(label in self.entity_types for label in entity1_labels)
                    entity2_match = any(entity in entity2_nn_chunk for entity in self.fixed_entities) and any(label in self.entity_types for label in entity2_labels)
                else:
                    entity1_match = any(label in self.entity_types for label in entity1_labels)
                    entity2_match = any(label in self.entity_types for label in entity2_labels)

                if entity1_match or entity2_match:
                    filtered_entities.append(entity_data)
            
        return [filtered_entities]