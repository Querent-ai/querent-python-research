import json
from llama_cpp import LlamaGrammar
import re

grammar = LlamaGrammar.from_file(file = "./querent/kg/rel_helperfunctions/subject_object_grammar.gbnf")

from llama_cpp import Llama
llm = Llama(model_path="./tests/llama-2-7b-chat.Q5_K_M.gguf")
context = "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca."
entity1 = "deposition"
entity2 = "a shale interval"
# entity1 = "the GoM basin"
# entity2 = "coarse-grained terrigenous material"
# output = llm.create_completion(
#       prompt=""""Please analyze the provided context and two entities
#         Context: We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca.
#         Entity 1: the GoM basin and Entity 2: coarse-grained terrigenous material
#         Query: Determine which entity is the subject and which is the object in the context along with the predicate between the entities. Please also identify the subject type, predicate type and object type.
#         Answer:""", grammar=grammar)
prompt = """Please analyze the provided context and the two named entities. Use this information to answer the query in provided json format. No Explanation needed and only fill the json required fields.
Context: {context}
Entity 1: {entity1}
Entity 2: {entity2}
Query: Determine which entity should be subject and which entity should be object based context along with the along with the predicate. Also identify the subject type, predicate type and object type. Output only in the below format.
Json Format:{{'subject': subject, 'object': object, 'subject_type': subject_type, 'object_type': object_type, 'predicate': predicate, 'predicate_type': predicate_type}}
Answer:""".format(context=context, entity1=entity1, entity2=entity2)

def extract_fields(text):
    # Define a dictionary to hold the extracted data
    data = {}

    # List of fields to extract
    fields = ["subject", "object", "subject_type", "object_type", "predicate", "predicate_type"]

    # Regular expression pattern for key-value pairs
    pattern = r'["\']({})["\']:\s*["\']([^"\']*)["\']'

    # Iterate over each field and use regex to find the corresponding value
    for field in fields:
        regex = pattern.format(field)
        match = re.search(regex, text)
        if match:
            data[field] = match.group(2)
        else:
            data[field] = None  # or 'Not found' or any default value

    return data

print("prompt", prompt)
output = llm.create_completion(
      prompt= prompt)
print(output)
choices_text = output['choices'][0]['text']
extracted_data = extract_fields(choices_text)
print(extracted_data)
