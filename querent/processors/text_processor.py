from unidecode import unidecode
import nltk
from nltk.corpus import words

from querent.processors.async_processor import AsyncProcessor
from querent.logging.logger import setup_logger


class TextProcessor(AsyncProcessor):
    def __init__(self):
        nltk.download("words")
        self.english_vocab = set(w.lower() for w in words.words())
        self.logger = setup_logger(__name__, "TextProcessor")

    async def process_text(self, data: str) -> str:
        try:
            if data is None or data == "":
                return [data]
            text = unidecode(data)

            processed_lines = []
            for line in text.split("\n"):
                words_in_line = line.split()
                i = 0
                new_line = ""
                while i < len(words_in_line):
                    word = words_in_line[i]
                    # Check if next word exists
                    if i + 1 < len(words_in_line):
                        next_word = words_in_line[i + 1]
                        combined_word = word + next_word
                        # Join words only if the combined form is valid and neither of the individual words is valid
                        if self.is_valid_word(combined_word) and not (
                            self.is_valid_word(word) or self.is_valid_word(next_word)
                        ):
                            word = combined_word
                            i += 1
                    new_line += word + " "
                    i += 1
                processed_lines.append(new_line.strip())
            return processed_lines
        except Exception as e:
            self.logger.error(f"Exception while processing data {e}")
            return []

    def is_valid_word(self, word):
        return word.lower() in self.english_vocab
