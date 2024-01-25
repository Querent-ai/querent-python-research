import spacy
import re
from typing import List
from nltk.corpus import wordnet as wn
import json

"""
    FixedPredicateExtractor is a class designed for extracting sentences containing specific predicates or predicate types from text. It utilizes spaCy for natural language processing and WordNet for synonym expansion.

    Key functionalities include:
    - Initialization with a list of fixed predicates, predicate types, and a spaCy model.
    - Extending the list of predicates with their synonyms from WordNet to capture variations in language.
    - Creation of a combined regular expression pattern for matching extended predicates in text.
    - Lemmatization of predicates for improved matching accuracy.
    - Extraction of sentences from the text that contain specified predicates.
    - Inclusion of contextual sentences adjacent to those with predicates for better context understanding.
    - Processing and filtering predicates based on specified predicate types and fixed predicates.

    This class is particularly useful in scenarios where the focus is on extracting relationships or actions (predicates) from text, and understanding the context in which these predicates are used.
    """


class FixedPredicateExtractor:
    def __init__(self, fixed_predicates: List[str] = None, predicate_types: List[str] = None, model=None):
        try:
            self.nlp = model
            self.predicate_types = predicate_types
            self.fixed_predicates = fixed_predicates

            if fixed_predicates:
                extended_predicates = self.extend_with_synonyms(fixed_predicates)
                self.predicate_pattern = self.create_combined_pattern(extended_predicates)
                self.lemmatized_predicates = set(self.lemmatize_predicates(extended_predicates))
        except Exception as e:
            raise Exception(f"Failed to initialize FixedPredicateExtractor: {e}")

    def get_wordnet_synonyms(self, word):
        try:
            synonyms = set()
            for synset in wn.synsets(word):
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    synonyms.add(synonym)
            return list(synonyms)
        except Exception as e:
            raise Exception(f"Error getting synonyms for word '{word}': {e}")

    def extend_with_synonyms(self, predicates):
        try:
            all_predicates = set(predicates)
            for predicate in predicates:
                synonyms = self.get_wordnet_synonyms(predicate)
                all_predicates.update(synonyms)
            return list(all_predicates)
        except Exception as e:
            raise Exception(f"Error extending predicates with synonyms: {e}")

    def create_combined_pattern(self, predicates):
        try:
            combined_pattern = '|'.join(map(re.escape, predicates))
            return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)
        except Exception as e:
            raise Exception(f"Error creating combined regex pattern: {e}")

    def lemmatize_predicates(self, predicates):
        try:
            return [self.nlp(predicate)[0].lemma_ for predicate in predicates]
        except Exception as e:
            raise Exception(f"Error lemmatizing predicates: {e}")

    def find_predicate_sentences(self, text: str) -> str:
        try:
            doc = self.nlp(text)
            relevant_sentences = []
            added_sentences = set()
            prev_sentence = None

            for j, sentence in enumerate(doc.sents):
                if self.is_predicate_present(sentence):
                    self.add_contextual_sentences(j, list(doc.sents), prev_sentence, relevant_sentences, added_sentences)
                prev_sentence = sentence

            return ' '.join(relevant_sentences)
        except Exception as e:
            raise Exception(f"Error finding predicate sentences in text: {e}")

    def add_contextual_sentences(self, j, sentences, prev_sentence, relevant_sentences, added_sentences):
        try:
            if prev_sentence and prev_sentence.text not in added_sentences:
                relevant_sentences.append(prev_sentence.text)
                added_sentences.add(prev_sentence.text)

            current_sentence = sentences[j]
            if current_sentence.text not in added_sentences:
                relevant_sentences.append(current_sentence.text)
                added_sentences.add(current_sentence.text)

            if j < len(sentences) - 1:
                next_sentence = sentences[j + 1]
                if next_sentence.text not in added_sentences:
                    relevant_sentences.append(next_sentence.text)
                    added_sentences.add(next_sentence.text)
        except Exception as e:
            raise Exception(f"Error adding contextual sentences: {e}")

    def is_predicate_present(self, sentence):
        try:
            sentence_text = sentence.text
            sentence_lemmas = {token.lemma_ for token in sentence}
            return self.fixed_predicates and (self.predicate_pattern.search(sentence_text) or sentence_lemmas.intersection(self.lemmatized_predicates))
        except Exception as e:
            raise Exception(f"Error checking predicate presence in sentence: {e}")

    def process_predicate_types(self, doc_predicates):
        try:
            filtered_predicates = []
            added_tuples = set() 

            for predicate_data in doc_predicates:
                predicate_phrase, json_data, object_phrase = predicate_data
                tuple_str = str(predicate_data)
                if tuple_str in added_tuples:
                    continue

                predicate_info = json.loads(json_data)
                predicate_type = predicate_info.get("predicate_type", "").lower()

                for user_defined_type in self.predicate_types:
                    if user_defined_type.lower() in predicate_type:
                        filtered_predicates.append(predicate_data)
                        added_tuples.add(tuple_str)
                        break

            return filtered_predicates
        except Exception as e:
            raise Exception(f"Error processing predicate types: {e}")