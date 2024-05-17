from querent.models.model import Model
from querent.models.model_factory import ModelFactory

class OpenAI4o(Model):
    """ A specific implementation of a Model for OPENAI4o language processing. """
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_instance = None

    def return_model_name(self):
        """ Returns the specific model name for the OPENAI4o model. """
        self.model_instance = "gpt-4o"
        return self.model_instance

class OPENAI4oFactory(ModelFactory):
    """ Factory for creating OPENAI 4o model instances. """
    def create(self, model_name: str) -> Model:
        return OpenAI4o(model_name)
    
    