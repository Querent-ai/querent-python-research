from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import SentenceTransformersTokenTextSplitter
from langchain.docstore.document import Document
from nltk.tokenize import sent_tokenize
import os


class EmbeddingStore:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', vector_store_path='./querent/kg/rel_helperfunctions/vectorstores/'):
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name, model_kwargs={'device': 'cpu'})
        self.vector_store_path = vector_store_path
        self.db = None

    def create_index(self, texts, verbose=False):
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
                print(f"Chunk {i+1}:")
                print(chunk)
                print("-----")

        return docs

    def save_index(self, file_name='FAISS_index'):
        file_path = os.path.join(self.vector_store_path, file_name)
        os.makedirs(self.vector_store_path, exist_ok=True)
        self.db.save_local(file_path)

    def load_index(self, file_name='FAISS_index'):
        file_path = os.path.join(self.vector_store_path, file_name)
        self.db = FAISS.load_local(file_path, self.embeddings)

    def as_retriever(self, search_type='similarity', search_kwargs={'k': 2}):
        if self.db is None:
            raise ValueError("FAISS index is not loaded. Call load_index() first.")
        
        return self.db.as_retriever(search_type=search_type, search_kwargs=search_kwargs)
    


# create_emb = EmbeddingStore(vector_store_path="/home/nishantg/querent-main/querent/querent/kg/rel_helperfunctions/vectorstores/")
# input = ['Abstract in this study, we present evidence of a paleoceneeocene thermal maximum (petm) record within a 543-m-thick (1780 ft) deep-marine section in the gulf of mexico (gom) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom.',
#          'We suggest that climate and tectonic perturbations in the upstream north american catchments can induce a substantial response in the downstream sectors of the gulf coastal plain and ultimately in the gom. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in the deep-sea fans of the gom basin. Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions.',
#          'This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the petm, and (2) a considerable increase in sedi- ment supply during the petm, which is archived as a particularly thick sedimentary section in the deep-sea fans of the gom basin. Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions. Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe.',
#          'Despite other thick petm sections being observed elsewhere in the world, the one described in this study links with a continental- scale paleo-drainage, which makes it of particular interest for paleoclimate and source- to-sink reconstructions. Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe. One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021).',
#          'Introduction the paleoceneeocene thermal maximum (petm) (ca. 56 ma) was a rapid global warming event characterized by the rise of temperatures to 59 c (kennett and stott, 1991), which caused substantial environmental changes around the globe. One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016).',
#          'One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.One effect was the intensification of the hydrologic cycle as a response to a changing atmospheric concentration of co2 (harper et al. , 2020; rush et al. , 2021). The petm is charac- terized by a negative carbon isotope excursion (cie) of roughly 3.0 that developed in <5 *e-mail: lucas. Vimpere@unige. Ch k. Y. (zeebe et al. , 2016). Three main phases of the cie have been formally identified (mciner- ney and wing, 2011): (1) the onset, defined as the time from the last samples with pre-cie car- bon isotope values to the most depleted ones; (2) the body, which represents the interval during which isotope values were low but constant; and (3) the recovery, during which carbon isotope values returned to pre-cie levels.']
# create_emb.create_index(texts=input, verbose=True)
# create_emb.save_index('my_FAISS_index')