import json
from llama_cpp import LlamaGrammar
import re

# grammar = LlamaGrammar.from_file(file = "./querent/kg/rel_helperfunctions/subject_object_grammar.gbnf")
grammar = LlamaGrammar.from_file(file = "./querent/kg/rel_helperfunctions/json.gbnf")

from llama_cpp import Llama
llm = Llama(model_path="./tests/llama-2-7b-chat.Q5_K_M.gguf", n_threads=3, use_mmap=False)
context = "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca."
# entity1 = "deposition"
# entity2 = "a shale interval"
entity1 = "the GoM basin"
entity2 = "coarse-grained terrigenous material"
output = llm.create_completion(
      prompt="""Please analyze the provided context and two entities
        Context: We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca.
        Entity 1: the GoM basin and Entity 2: coarse-grained terrigenous material
        Query: Determine which entity is the subject and which is the object in the context along with the predicate between the entities. Please also identify the subject type, predicate type and object type.
        Answer:""", grammar=grammar)


print(output)
choices_text = output['choices'][0]['text']
extracted_data = choices_text
print(extracted_data)
