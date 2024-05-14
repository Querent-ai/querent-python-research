from querent.models.model import Model
from querent.models.model_factory import ModelFactory


class English(Model):
    """ A specific implementation of a Model for English language processing. """
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_instance = None

    def return_model_name(self):
        """ Returns the specific model name for the English model. """
        self.model_instance = "dbmdz/bert-large-cased-finetuned-conll03-english"
        return self.model_instance

class EnglishFactory(ModelFactory):
    """ Factory for creating English model instances. """
    def create(self, model_name: str) -> Model:
        return English(model_name)


