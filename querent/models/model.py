from abc import ABC, abstractmethod

class Model(ABC):
    """ Abstract base class for all models. """
    def __init__(self, model_name):
        self.model_name = model_name

    @abstractmethod
    def return_model_name(self):
        """ Return the model name, to be implemented by all subclasses. """
        pass
