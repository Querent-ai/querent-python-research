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
            lines = text.split("\n")
            for index, line in enumerate(lines):
                words_in_line = line.split()
                i = 0
                new_line = ""
                while i < len(words_in_line):
                    word = words_in_line[i]
                    # Check if next word exists
                    if i + 1 < len(words_in_line) and i > 0:
                        next_word = words_in_line[i + 1]
                        prev_word = words_in_line[i - 1]
                        combined_next_word = word + next_word
                        combined_prev_word = prev_word + word
                        # Join words only if the combined form is valid and neither of the individual words is valid
                        if self.is_valid_word(combined_next_word) and not (
                            self.is_valid_word(word) or self.is_valid_word(next_word)
                        ):
                            word = combined_next_word
                            i += 1
                        elif self.is_valid_word(combined_prev_word) and not (
                            self.is_valid_word(word) or self.is_valid_word(prev_word)
                        ):
                            # If individual word formed after joining current word and previous word is valid, then delete the previous word and replace it with new word

                            word = combined_prev_word
                            last_space_index = new_line.rfind(" ")
                            if last_space_index != -1:
                                second_last_space_index = new_line.rfind(
                                    " ", 0, last_space_index
                                )
                                if second_last_space_index == -1:
                                    second_last_space_index = 0
                                new_line = (
                                    new_line[:second_last_space_index]
                                    + new_line[last_space_index:]
                                )
                    new_line += word + " "
                    i += 1

                if (
                    len(line) > 3
                    and index < len(lines) - 1
                    and words_in_line[len(words_in_line) - 1] == "-"
                ):
                    # If the sentence ends with hyphen(-), then check if the word is incomplete, if yes then join them
                    current_word = words_in_line[len(words_in_line) - 2]
                    next_index = lines[index + 1].index(" ")
                    next_word = lines[index + 1][:next_index]
                    new_word = current_word + next_word
                    if self.is_valid_word(new_word):
                        new_line = new_line[: len(new_line) - 3] + next_word
                        lines[index + 1] = lines[index + 1][next_index + 1 :]

                processed_lines.append(new_line.strip())

            return processed_lines
        except Exception as e:
            self.logger.error(f"Exception while processing data {e}")
            return []

    def is_valid_word(self, word):
        return word.lower() in self.english_vocab
