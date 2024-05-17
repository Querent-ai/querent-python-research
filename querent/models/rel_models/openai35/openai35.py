from querent.models.model import Model
from querent.models.model_factory import ModelFactory

class OpenAI35(Model):
    """ A specific implementation of a Model for OpenAI35 language processing. """
    def __init__(self, model_name):
        super().__init__(model_name)
        self.model_instance = None

    def return_model_name(self):
        """ Returns the specific model name for the OpenAI35 model. """
        self.model_instance = "gpt-3.5-turbo"
        return self.model_instance

class OpenAI35Factory(ModelFactory):
    """ Factory for creating OPENAI 3.5 model instances. """
    def create(self, model_name: str) -> Model:
        return OpenAI35(model_name)
    
    