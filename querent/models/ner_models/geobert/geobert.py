from querent.models.model import Model
from querent.models.model_factory import ModelFactory

class GeoBERT(Model):
    """ A specific implementation of a Model for GeoBERT NER. """
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_instance = None

    def return_model_name(self):
        """ Returns the specific model name GeoBERT model. """
        self.model_instance = "botryan96/GeoBERT"
        return self.model_instance


class GeoBERTFactory(ModelFactory):
    """ Factory for creating English model instances. """
    def create(self, model_name: str) -> Model:
        return GeoBERT(model_name)