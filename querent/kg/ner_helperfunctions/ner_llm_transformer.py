from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch
import nltk
from nltk.tokenize import sent_tokenize
from typing import Any, List, Tuple
from querent.logging.logger import setup_logger
import os
from querent.kg.ner_helperfunctions.dependency_parsing import Dependency_Parsing


# nltk.data.path.append(
#     "/home/nishantg/querent/querent/nltk_resources/"
# )  ##need to configure still

"""
    Named Entity Recognition (NER) class for extracting entities and relationships from text.

    Attributes:
        ner_tokenizer (Tokenizer): Tokenizer for the NER model.
        ner_model (Model): Pre-trained NER model.
        logger (Logger): Logger instance for logging errors and information.

    Methods:
        tokenize_sentence(sentence: str) -> List[str]:
            Tokenizes a given sentence into individual tokens.

        get_chunks(tokens: List[str]) -> List[List[str]]:
            Splits tokens into smaller chunks for processing.

        extract_entities_from_chunk(chunk: List[str]) -> List[dict]:
            Extracts entities from a given chunk of tokens.

        combine_entities_wordpiece(entities: List[dict], tokens: List[str]) -> List[dict]:
            Combines entities that are split due to wordpiece tokenization.

        extract_binary_pairs(entities: List[dict], tokens: List[str], all_sentences: List[str], sentence_idx: int) -> List[Tuple[Tuple[dict, dict], dict]]:
            Extracts binary pairs of entities from the given entities list.

        extract_entities_from_sentence(sentence: str, sentence_idx: int, all_sentences: List[str]) -> Tuple[List[dict], List[Tuple[Tuple[dict, dict], dict]]]:
            Extracts entities and binary pairs from a given sentence.

        _token_distance(tokens: List[str], start_idx1: int, start_idx2: int, noun_chunk1: List[str], noun_chunk2: List[str]) -> int:
            Calculates the token distance between two entities.
    """


class NER_LLM:
    def __init__(
        self, ner_model_name="dbmdz/bert-large-cased-finetuned-conll03-english",
        filler_tokens=None,
        provided_tokenizer=None,
        provided_model=None
    ):
        self.logger = setup_logger(__name__, "NER_LLM")
        if provided_tokenizer:
            self.ner_tokenizer = provided_tokenizer
        else:
            self.ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
        if provided_model:
            self.ner_model = provided_model
        else:
            self.ner_model = NER_LLM.load_model(ner_model_name, "NER")
        self.filler_tokens = filler_tokens or ["of", "a", "the", "in", "on", "at", "and", "or", "with","(",")","-"]

    def load_model(model_name, model_type):
        """Load the model, handling potential TensorFlow weights."""
        try:
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU if there's an issue
            return AutoModelForTokenClassification.from_pretrained(model_name, output_attentions=True)
        except OSError as e:
            os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU if there's an issue
            ##print("GPU turned offffffffff")
            if "file named pytorch_model.bin" in str(e) and "file for TensorFlow weights" in str(e):
                return AutoModelForTokenClassification.from_pretrained(model_name, from_tf=True)
            raise OSError(
                f"Failed to load {model_type} model from {model_name}. Error: {e}"
            )
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while loading the model: {e}"
            )

    def validate(self) -> bool:
        return self.ner_model is not None and self.ner_tokenizer is not None

    @staticmethod
    def split_into_sentences(document) -> List[str]:
        document = document.replace("\n", " ")
        sentences = []
        try:
            sentences = sent_tokenize(document)
        except Exception as e:
            raise Exception(
                f"An unexpected error occurred while splitting the document into sentences: {e}"
            )

        return sentences

    def tokenize_sentence(self, sentence: str):
        return self.ner_tokenizer.tokenize(sentence)

    def _tokenize_and_chunk(self, data: str) -> List[Tuple[List[str], str, int]]:
        try:
            sentences = self.split_into_sentences(data)
            tokenized_sentences = []
            for idx, sentence in enumerate(sentences):
                sentence_tokens = self.tokenize_sentence(sentence)
                tokenized_sentences.append((sentence_tokens, sentence, idx))
        except Exception as e:
            raise Exception(f"An error occurred while tokenizing: {e}")

        return tokenized_sentences

    def _token_distance(self, tokens, start_idx1, start_idx2, noun_chunk1, noun_chunk2):
        distance = 0
        for idx in range(start_idx1 + 1, start_idx2):
            token = tokens[idx]
            if (token not in self.filler_tokens and
                token not in noun_chunk1 and
                token not in noun_chunk2 and
                not token.startswith('##')):
                distance += 1
        return distance


    def transform_entity_pairs(self, entity_pairs):
        transformed_pairs = []
        sentence_group = {}
        for pair, metadata in entity_pairs:
            combined_sentence = ' '.join(filter(None, [
                metadata['previous_sentence'],
                metadata['current_sentence'],
                metadata['next_sentence']
            ]))
            if combined_sentence not in sentence_group:
                sentence_group[combined_sentence] = []
            sentence_group[combined_sentence].append(pair)

        for combined_sentence, pairs in sentence_group.items():
            for entity1, entity2 in pairs:
                meta_dict = {
                    "entity1_score": entity1['score'],
                    "entity2_score": entity2['score'],
                    "entity1_label": entity1['label'],
                    "entity2_label": entity2['label'],
                    "entity1_nn_chunk":entity1['noun_chunk'],
                    "entity2_nn_chunk":entity2['noun_chunk'],
                }
                new_pair = (entity1['entity'], combined_sentence, entity2['entity'], meta_dict)
                transformed_pairs.append(new_pair)

        return transformed_pairs

    def get_chunks(self, tokens: List[str], max_chunk_size=510):
        chunks = []
        k = 0
        while k < len(tokens):
            end = min(k + max_chunk_size, len(tokens))
            while end > k and end < len(tokens) and tokens[end].startswith("##"):
                end -= 1
            chunks.append(tokens[k:end])
            k = end
        return chunks

    def extract_entities_from_chunk(self, chunk: List[str]):
        results = []
        try:
            input_ids = self.ner_tokenizer.convert_tokens_to_ids(chunk)
            input_tensor = torch.tensor([input_ids])
            with torch.no_grad():
                outputs = self.ner_model(input_tensor)
            predictions = torch.argmax(outputs[0], dim=2)
            scores = torch.nn.functional.softmax(outputs[0], dim=2)
            label_ids = predictions[0].tolist()
            label_list = self.ner_model.config.id2label
            for idx, label_id in enumerate(label_ids):
                label = label_list[label_id]
                if label not in ["O", "[CLS]", "[SEP]", "[PAD]"]:
                    entity_info = {
                        "entity": chunk[idx],
                        "label": label,
                        "score": scores[0][idx][label_id].item(),
                        "start_idx": idx
                    }
                    results.append(entity_info)
        except Exception as e:
            self.logger.error(f"Error extracting entities from chunk: {e}")
            raise
        return results

    def combine_entities_wordpiece(self, entities: List[dict], tokens: List[str]):
        combined_entities = []
        i = 0
        while i < len(entities):
            entity = entities[i]
            while i + 1 < len(entities) and entities[i + 1]["entity"].startswith("##"):
                entity["entity"] += entities[i + 1]["entity"][2:]
                entity["score"] = (entity["score"] + entities[i + 1]["score"]) / 2
                i += 1
            combined_entities.append(entity)
            i += 1
        final_entities = []
        for entity in combined_entities:
            entity_text = entity["entity"]
            start_idx = entity["start_idx"]
            while entity_text.startswith("##"):
                start_idx -= 1
                entity_text = tokens[start_idx] + entity_text[2:]
            entity["entity"] = entity_text
            final_entities.append(entity)

        return final_entities
    
    def combine_entities_byteencoding(self, entities: List[dict], tokens: List[str]):
        combined_entities = []
        i = 0
        while i < len(entities):
            entity = entities[i]
            while entity["start_idx"] > 0 and not tokens[entity["start_idx"]].startswith("▁"):
                entity["start_idx"] -= 1
                entity["entity"] = tokens[entity["start_idx"]] + entity["entity"]
            while i + 1 < len(entities) and entities[i + 1]["start_idx"] == entity["start_idx"] + 1 and not entities[i + 1]["entity"].startswith("▁"):
                entity["entity"] += entities[i + 1]["entity"]
                entity["score"] = (entity["score"] + entities[i + 1]["score"]) / 2
                i += 1
            combined_entities.append(entity)
            i += 1

        final_entities = []
        for entity in combined_entities:
            entity_text = entity["entity"]
            if entity_text.startswith("▁"):
                entity_text = entity_text[1:]
            entity["entity"] = entity_text
            final_entities.append(entity)

        return final_entities

    def extract_binary_pairs(self, entities: List[dict], tokens: List[str], all_sentences: List[str], sentence_idx: int):
        binary_pairs = []
        try:
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    if entities[i]["start_idx"] + 1 == entities[j]["start_idx"]:
                        continue
                    distance = self._token_distance(tokens, entities[i]["start_idx"], entities[j]["start_idx"],entities[i]["noun_chunk"], entities[j]["noun_chunk"])
                    if distance <= 15:
                        pair = (entities[i], entities[j])
                        if pair not in binary_pairs:
                            metadata = {
                                "current_sentence": all_sentences[sentence_idx],
                                "previous_sentence": all_sentences[sentence_idx - 1] if sentence_idx > 0 else None,
                                "next_sentence": all_sentences[sentence_idx + 1] if sentence_idx < len(all_sentences) - 1 else None
                            }
                            binary_pairs.append((pair, metadata))
        except Exception as e:
            self.logger.error(f"Error extracting binary pairs: {e}")
            raise
        return binary_pairs

    def extract_entities_from_sentence(self, sentence: str, sentence_idx: int, all_sentences: List[str]):
        try:
            tokens = self.tokenize_sentence(sentence)
            chunks = self.get_chunks(tokens)
            all_entities = []
            for chunk in chunks:
                entities = self.extract_entities_from_chunk(chunk)
                all_entities.extend(entities)
            final_entities = self.combine_entities_wordpiece(all_entities, tokens)
            #final_entities = self.combine_entities_byteencoding(all_entities, tokens)
            parsed_entities = Dependency_Parsing(entities=final_entities, sentence=sentence)
            binary_pairs = self.extract_binary_pairs(parsed_entities.entities, tokens, all_sentences, sentence_idx)
            return parsed_entities.entities, binary_pairs
        except Exception as e:
            self.logger.error(f"Error extracting entities from sentence: {e}")
            raise


ner_llm = NER_LLM(ner_model_name="botryan96/GeoBERT")



# is_valid = ner_llm.validate()
# print(f"Model and tokenizer validation: {is_valid}")
# document = """ABSTRACT
# In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM)
# record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM)
# using organic carbon stable isotopes and biostratigraphic constraints."""

# tokens = ner_llm._tokenize_and_chunk(document)
# print("Tokens List:", tokens)
# for tokenized_sentence, original_sentence, sentence_idx in tokens:
# #   print(tokenized_sentence)
# #   print(original_sentence)
# #   print(sentence_idx)
# #   print("[s[1] for s in tokens]", [s[1] for s in tokens] )
#     entities, entity_pairs = ner_llm.extract_entities_from_sentence(original_sentence, sentence_idx, [s[1] for s in tokens])
#     #print("entity pairs : ", entity_pairs)
#     transformed_pairs = ner_llm.transform_entity_pairs(entity_pairs)
#     print(transformed_pairs)
#     # for tup in transformed_pairs:
#     #     entity1 = tup[0]
#     #     entity2 = tup[2]
#     #     print(f"Entity1: {entity1}")
#     #     print(f"Entity2: {entity2}")
#     #     print("------")

#document = "Nishant is working from Delhi. Ansh is working from Punjab."
# # Initialize the tokenizer and model outside the NER_LLM class
# tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
# model = AutoModelForTokenClassification.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")

# tokenizer = AutoTokenizer.from_pretrained("botryan96/GeoBERT")
# #model = AutoModelForTokenClassification.from_pretrained("botryan96/GeoBERT")

# # Pass the initialized tokenizer and model to the NER_LLM class
# ner_llm = NER_LLM(provided_tokenizer=tokenizer, ner_model_name="botryan96/GeoBERT")



#More models to try 
# "spacy"
# "dslim/bert-base-NER" 
# "botryan96/GeoBERT" 
# "QCRI/bert-base-multilingual-cased-pos-english" ## POS - need to determine its use case
# "xlm-roberta-large-finetuned-conll03-english"
# "Jean-Baptiste/roberta-large-ner-english"
# implement https://huggingface.co/tner/roberta-large-ontonotes5
# allenai/scibert_scivocab_uncased
# LSTM and Bi-LSTM ?
 # dbmdz/bert-large-cased-finetuned-conll03-english

