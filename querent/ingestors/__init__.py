from abc import ABC, abstractmethod



class BaseDataIngestor(ABC):
    """
    Base class for Data Ingestor
    """
    @abstractmethod
    def ingest_some_data():
        pass





class AWSIngestor(BaseDataIngestor):
    def ingest_some_data(self):
        injestor = aws_data_ingestor()
        pass




class GCPIngestor(BaseDataIngestor):
    def ingest_some_data(self):
        pass



class WebScraperIngestor(BaseDataIngestor):
    def ingest_some_data(self):
        pass



#optional 
class DataProcessor(ABC):
    """
    Base class for data tokenization 
    """
    @abstractmethod
    def process_some_data(self):
        pass



class WebScraperProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass


class AWSProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass


class GCPProcessor(BaseDataProcessor):
    def process_some_data(self):
        pass
