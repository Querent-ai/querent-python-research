from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain.docstore.document import Document
from nltk.tokenize import sent_tokenize
import os

from querent.logging.logger import setup_logger

"""
    A class for creating and managing an embedding-based document store using FAISS (Facebook AI Similarity Search).

    This class utilizes sentence-transformer embeddings to vectorize text and store it in a FAISS index for 
    efficient similarity searches. It supports creating the index from a list of texts, saving and loading the 
    index, and retrieving documents based on similarity queries.

    Attributes:
        model_name (str): The name of the model used for generating embeddings. Defaults to 
                          'sentence-transformers/all-MiniLM-L6-v2'.
        embeddings (HuggingFaceEmbeddings): An instance of HuggingFaceEmbeddings for embedding extraction.
        vector_store_path (str): The path to save or load the FAISS index files.
        db (FAISS): The FAISS index instance.

    Methods:
        create_index(texts, verbose=False): Creates a FAISS index from a list of texts.
            Parameters:
                texts (list of str): The texts to be indexed.
                verbose (bool): If True, prints information about the chunks being indexed.

        save_index(file_name='FAISS_index'): Saves the FAISS index to a file.
            Parameters:
                file_name (str): The name of the file to save the index. Defaults to 'FAISS_index'.

        load_index(file_name='FAISS_index'): Loads a FAISS index from a file.
            Parameters:
                file_name (str): The name of the file to load the index. Defaults to 'FAISS_index'.

        as_retriever(search_type='similarity', search_kwargs={'k': 2}): Provides a retriever for performing 
        searches on the index.
            Parameters:
                search_type (str): The type of search to perform ('similarity' or other types supported by FAISS).
                search_kwargs (dict): Additional keyword arguments for the search function.
            Returns:
                A retriever instance configured for the specified search type and parameters.
    """

class EmbeddingStore:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', vector_store_path='./querent/kg/rel_helperfunctions/vectorstores/'):
        self.logger = setup_logger("EmbeddingStore_config", "EmbeddingStore")
        try:
            self.model_name = model_name
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
            self.vector_store_path = vector_store_path
            self.db = None
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize EmbeddingStore: {e}")
            raise Exception(f"Failed to initialize EmbeddingStore: {e}")


    def create_index(self, texts, verbose=False):
        try:
            text_splitter = SentenceTransformersTokenTextSplitter(chunk_overlap=0)
            final_chunks = []
            for text in texts:
                sentences = sent_tokenize(text)
                current_chunk = ""
                for sentence in sentences:
                    token_count = text_splitter.count_tokens(text=current_chunk + sentence)
                    if token_count > 250:
                        if current_chunk:
                            final_chunks.append(current_chunk)
                        current_chunk = sentence
                    else:
                        current_chunk += (" " + sentence).strip()
                if current_chunk:
                    final_chunks.append(current_chunk)

            docs = [Document(page_content=x) for x in final_chunks]
            self.db = FAISS.from_documents(docs, self.embeddings)

            if verbose:
                for i, chunk in enumerate(final_chunks):
                    self.logger.info("Embedding Store Chunk %i: %s", i, chunk)

            return docs
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to create index: {e}")
            raise Exception(f"Failed to create index: {e}")

    def save_index(self, file_name='FAISS_index'):
        try:
            file_path = os.path.join(self.vector_store_path, file_name)
            os.makedirs(self.vector_store_path, exist_ok=True)
            self.db.save_local(file_path)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to save index: {e}")
            raise Exception(f"Failed to save index: {e}")

    def load_index(self, file_name='FAISS_index'):
        try:
            file_path = os.path.join(self.vector_store_path, file_name)
            self.db = FAISS.load_local(file_path, self.embeddings)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to load index: {e}")
            raise Exception(f"Failed to load index: {e}")

    def as_retriever(self, search_type='similarity', search_kwargs={'k': 10}):
        try:
            if self.db is None:
                raise ValueError("FAISS index is not loaded. Call load_index() first.")
            return self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
        except Exception as e:
            self.logger.error(f"Invalid {self.__class__.__name__} configuration. Failed to initialize retriever: {e}")
            raise Exception(f"Failed to initialize retriever: {e}")
    
# create_emb = EmbeddingStore(vector_store_path="/home/nishantg/querent-main/querent/querent/kg/rel_helperfunctions/vectorstores/")
# input = ['Abstract in this study, we present evidence of a paleoceneeocene thermal maximum (petm) record within a 543-m-thick (1780 ft) deep-marine section in the gulf of mexico (gom) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom.',
#          'We suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in the deep-sea fans of the gom basin. Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions.',
#          'This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in the deep-sea fans of the gom basin. Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions. Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe.',
#          'Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions. Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe. One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021).',
#          'Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe. One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016).',
#          'One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.',
#          'Three main phases of the CIE have been formally identified (McInerney and Wing, 2011): (1) the “onset”, defined as the time from the last samples with pre-CIE carbon isotope values to the most depleted ones; (2) the “body”, which represents the interval during which isotope values were low but constant; and (3) the “recovery”, during which carbon isotope values returned to pre-CIE levels.Together with a drastic increase of the dinoflagellate cyst Apectodinium spp. abundance(Crouch et al., 2001) and a generalized dissolution of carbonates, it has been interpreted that large amounts of 13C-depleted carbon had been released into the oceans and the atmosphere(Dickens et al., 1997). The distinctive CIE has been identified in a wide range of environments,from continental deposits to deep-water sedi-ments (Khozyem et al., 2013), but its source is still under debate.',
#          'The distinctive CIE has been identified in a wide range of environments,from continental deposits to deep-water sediments (Khozyem et al., 2013), but its source is still under debate. The currently proposed hypotheses include volcanic emissions (Gutjahret al., 2017), organic carbon from land plants and soils (Bowen, 2013) or biogenic methane (Dickens et al., 1997), or a combination of the latter two (Higgins and Schrag, 2006). The Gulf of Mexico (GoM) is bounded by the southern coast of North America to the north, the Tampico, Vera Cruz, and Tabasco regions of Mexico to the west and south, and the Yucatán and Florida platforms to the east.']
# create_emb.create_index(texts=input, verbose=True)
# create_emb.save_index('my_FAISS_index')