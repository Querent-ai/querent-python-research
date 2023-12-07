# import os
# import pytest
# from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
# import shutil

# @pytest.fixture(scope="function")
# def embedding_store():
#     my_directory_path = './tests/kg_tests/vectorstores/'
#     store = EmbeddingStore(vector_store_path=my_directory_path)
#     yield store

# def test_create_and_save_index(embedding_store):
#     sentences = """In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM)
# using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce
# a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom-
# modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi-
# ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin. Despite other thick PETM sections being
# observed elsewhere in the world, the one described in this study links with a continental-scale paleo-drainage, which makes it of particular interest for paleoclimate and source-
# to-sink reconstructions."""
    
#     embedding_store.create_index(sentences,verbose=True)
#     index_base_name = 'my_FAISS_index'
#     embedding_store.save_index(index_base_name)
#     index_faiss_path = os.path.join(embedding_store.vector_store_path, "my_FAISS_index", "index.faiss")
#     index_pkl_path = os.path.join(embedding_store.vector_store_path, "my_FAISS_index", "index.pkl")
#     # Assert that both files exist
#     assert os.path.isfile(index_faiss_path), "FAISS index file was not created."
#     assert os.path.isfile(index_pkl_path), "Pickle index file was not created."
#     # If the assertions pass, delete the my_FAISS_index folder
#     index_directory_path = os.path.join(embedding_store.vector_store_path, "my_FAISS_index")
#     if os.path.isdir(index_directory_path):
#         shutil.rmtree(index_directory_path)