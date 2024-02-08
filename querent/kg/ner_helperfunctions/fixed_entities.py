import re
from typing import List

"""
    FixedEntityExtractor is a class designed to extract specific entities and their related sentences from a given text. It uses spaCy for natural language processing and regular expressions for pattern matching.

    Key functionalities include:
    - Initialization with a list of fixed entities, entity types, and a spaCy model.
    - Creation of a combined regular expression pattern to match fixed entities in text.
    - Lemmatization of provided entities for better matching accuracy.
    - Extraction of sentences containing the specified entities from the provided text.
    - Ability to include contextual sentences adjacent to those containing the entities.
    - Calculation of text reduction percentage when filtering sentences.
    - Processing and filtering entity pairs based on specified entity types and fixed entities.

    This class is particularly useful for scenarios where only certain types of entities or specific named entities are of interest in a larger text.
    """

class FixedEntityExtractor:
    def __init__(self, fixed_entities: List[str] = None, entity_types: List[str] = None, model=None):
        try:
            self.nlp = model
        except Exception as e:
            raise Exception(f"Error loading spaCy model: {e}")

        self.entity_types = entity_types
        self.fixed_entities = fixed_entities

        if fixed_entities:
            try:
                self.entity_pattern = self.create_combined_pattern(fixed_entities)
                self.lemmatized_entities = set(self.lemmatize_entities(fixed_entities))
            except Exception as e:
                raise Exception(f"Error in processing fixed entities: {e}")

    def create_combined_pattern(self, entities):
        try:
            combined_pattern = '|'.join(map(re.escape, entities))
            return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)
        except Exception as e:
            raise Exception(f"Error creating combined pattern: {e}")

    def lemmatize_entities(self, entities):
        try:
            return [self.nlp(entity)[0].lemma_ for entity in entities]
        except Exception as e:
            raise Exception(f"Error in lemmatizing entities: {e}")

    def find_entity_sentences(self, text: str, chunk_size=1000) -> str:
        try:
            doc = self.nlp(text)
        except Exception as e:
            raise Exception(f"Error processing text with spaCy: {e}")

        relevant_sentences = []
        added_sentences = set()
        prev_sentence = None
        for j, sentence in enumerate(doc.sents):
            try:
                if self.is_entity_present(sentence):
                    self.add_contextual_sentences(list(doc.sents), j, prev_sentence, relevant_sentences, added_sentences)
            except Exception as e:
                raise Exception(f"Error while checking entity presence and adding contextual sentences: {e}")

            prev_sentence = sentence

        return ' '.join(relevant_sentences)

    def is_entity_present(self, sentence):
        try:
            sentence_text = sentence.text
            sentence_lemmas = {token.lemma_ for token in sentence}
            return self.fixed_entities and (self.entity_pattern.search(sentence_text) or sentence_lemmas.intersection(self.lemmatized_entities))
        except Exception as e:
            raise Exception(f"Error in checking if entity is present: {e}")


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
        try:
            filtered_entities = []
            def matches_criteria(entity_chunk, entity_labels):
                entity_chunk_lower = entity_chunk.lower()
                if self.fixed_entities:
                    fixed_entities_lower = [entity.lower() for entity in self.fixed_entities]
                    return any(entity in entity_chunk_lower for entity in fixed_entities_lower) and \
                        any(label in self.entity_types for label in entity_labels)
                return any(label in self.entity_types for label in entity_labels)


            for entity_group in doc_entities:
                for entity_data in entity_group:
                    entity1, sentence, entity2, entity_info = entity_data

                    entity1_labels = entity_info.get('entity1_label', '').split(', ')
                    entity2_labels = entity_info.get('entity2_label', '').split(', ')
                    entity1_nn_chunk = entity_info.get('entity1_nn_chunk', '')
                    entity2_nn_chunk = entity_info.get('entity2_nn_chunk', '')
                    entity1_match = matches_criteria(entity1_nn_chunk, entity1_labels)
                    entity2_match = matches_criteria(entity2_nn_chunk, entity2_labels)
                    if entity1_match or entity2_match:
                        filtered_entities.append(entity_data)

            return [filtered_entities]
        except Exception as e:
            raise Exception(f"Error in processing entity types: {e}")