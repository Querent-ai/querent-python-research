# from huggingface_hub import InferenceClient
# # client = InferenceClient(model = "botryan96/GeoBERT", token="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")

# # tokens = client.token_classification("In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe.")
# # print ("Tokens Produced ------------------------------------", tokens)
# # text = "In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe."
# text = "I am Nishant."
# # from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
# inference_api_key ="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"
# # API_TOKEN="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"
# # import requests

# # API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
# # headers = {"Authorization": f"Bearer {API_TOKEN}"}

# # def query(payload):
# # 	response = requests.post(API_URL, headers=headers, json=payload)
# # 	return response.json()
	
# # output = query({
# # 	"inputs": "Today is a sunny day and I will get some ice cream.",
# #     "options": {"wait_for_model": True}
# # })
# # print(output)
# from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

# embeddings = HuggingFaceInferenceAPIEmbeddings(api_key= inference_api_key, model_name="sentence-transformers/all-MiniLM-L6-v2")
# emb = embeddings.embed_query(text)
# print(emb)