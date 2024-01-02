import spacy
import re
from typing import List
from nltk.corpus import wordnet as wn
from nltk.tokenize import PunktSentenceTokenizer
import json

class FixedPredicateExtractor:
    def __init__(self, fixed_predicates: List[str] = None, predicate_types: List[str] = None, model="en_core_web_lg"):
        self.nlp = spacy.load(model)
        self.sentence_tokenizer = PunktSentenceTokenizer()
        self.predicate_types = predicate_types
        self.fixed_predicates = fixed_predicates

        if fixed_predicates:
            extended_predicates = self.extend_with_synonyms(fixed_predicates)
            self.predicate_pattern = self.create_combined_pattern(extended_predicates)
            self.lemmatized_predicates = set(self.lemmatize_predicates(extended_predicates))

    def get_wordnet_synonyms(self, word):
        synonyms = set()
        for synset in wn.synsets(word):
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                synonyms.add(synonym)
                
        return list(synonyms)
    
    def extend_with_synonyms(self, predicates):
        all_predicates = set(predicates)
        for predicate in predicates:
            synonyms = self.get_wordnet_synonyms(predicate)
            all_predicates.update(synonyms)
            
        return list(all_predicates)

    def create_combined_pattern(self, predicates):
        combined_pattern = '|'.join(map(re.escape, predicates))
        return re.compile(r'\b(?:' + combined_pattern + r')\b', re.IGNORECASE)

    def lemmatize_predicates(self, predicates):
        return [self.nlp(predicate)[0].lemma_ for predicate in predicates]

    def find_predicate_sentences(self, text: str) -> str:
        doc = self.nlp(text)
        relevant_sentences = []
        added_sentences = set()
        
        prev_sentence = None

        for j, sentence in enumerate(doc.sents):
            if self.is_predicate_present(sentence):
                self.add_contextual_sentences(j, list(doc.sents), prev_sentence, relevant_sentences, added_sentences)

            prev_sentence = sentence

        return ' '.join(relevant_sentences)

    def add_contextual_sentences(self, j, sentences, prev_sentence, relevant_sentences, added_sentences):
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

    def is_predicate_present(self, sentence):
        sentence_text = sentence.text
        sentence_lemmas = {token.lemma_ for token in sentence}
        return self.fixed_predicates and (self.predicate_pattern.search(sentence_text) or sentence_lemmas.intersection(self.lemmatized_predicates))

    def process_predicate_types(self, doc_predicates):
        filtered_predicates = []
        added_tuples = set()  # Set to track added tuples

        for predicate_data in doc_predicates:
            predicate_phrase, json_data, object_phrase = predicate_data

            # Convert tuple to a string for easy comparison
            tuple_str = str(predicate_data)

            # Skip this tuple if it has already been added
            if tuple_str in added_tuples:
                continue

            # Parse the JSON string to extract predicate type
            predicate_info = json.loads(json_data)
            predicate_type = predicate_info.get("predicate_type", "").lower()

            # Flexible matching of predicate types
            for user_defined_type in self.predicate_types:
                if user_defined_type.lower() in predicate_type:
                    filtered_predicates.append(predicate_data)
                    added_tuples.add(tuple_str)  # Add to set to track it has been added
                    break

        return filtered_predicates