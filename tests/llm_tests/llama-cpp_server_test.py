# import json
# from enum import Enum
# from typing import Union, Optional

# import requests
# from pydantic import BaseModel, Field

# import importlib
# from .pydantic_models_to_grammar import generate_gbnf_grammar_from_pydantic_models, generate_gbnf_grammar_and_documentation
# import concurrent.futures

# # Function to get completion on the llama.cpp server with grammar.
# def create_completion(prompt, grammar, n_predict):
#     headers = {"Content-Type": "application/json"}
#     data = {"prompt": prompt, "n_predict": n_predict, "temperature": 0}

#     response = requests.post("http://localhost:8080/completion", headers=headers, json=data)
#     data = response.json()
#     print(data)

#     print(data["content"])
#     return data["content"]

# def send_api_request(prompt):
#     headers = {"Content-Type": "application/json"}
#     data = {"prompt": prompt, "n_predict": 128, "temperature": 0}
    
#     response = requests.post("http://localhost:8080/completion", headers=headers, json=data)
#     response_data = response.json()
#     return response_data

# from pydantic import BaseModel, Field

# class Semantic_Triple(BaseModel):
#     """
#     Represents a semantic triple for controlling LLAMA output.
#     A semantic triple consists of a subject, subject type, object, object type,
#     predicate, and predicate type, allowing fine-grained control over language generation.
#     """
#     subject: str = Field(..., description="The subject of the semantic triple.")
#     subject_type: str = Field(..., description="The type of the subject.")
#     object: str = Field(..., description="The object of the semantic triple.")
#     object_type: str = Field(..., description="The type of the object.")
#     predicate: str = Field(..., description="The predicate of the semantic triple.")
#     predicate_type: str = Field(..., description="The type of the predicate.")



# gbnf_grammar, documentation = generate_gbnf_grammar_and_documentation([Semantic_Triple])

# # print("----------------------", gbnf_grammar)
# # print(documentation)
# # # JSON_Format: {{'subject': Subject, 'object': Object, 'predicate': Predicate, 'subject_type':Subject_Type, 'object_type':Object_Type, 'predicate_type':Predicate_Type  }}
# # # system_message = "You are an advanced AI, tasked to assist the user by calling functions in JSON format. The following are the available functions and their parameters and types:\n\n" + documentation
# prompt="""Please analyze the provided context and two entities. Only fill the values in place of output fields marked with {{output}} for the each respective key in the Json format described below and no need for any explanation.
# JSON_Format: {{'subject': {{output}}, 'object': {{output}}, 'predicate': {{output}}, 'subject_type':{{output}}, 'object_type':{{output}}, 'predicate_type':{{output}} }}
# Context: We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca.
# Entity 1: the GoM basin and Entity 2: coarse-grained terrigenous material
# Query: Determine which entity is the subject and which is the object in the context, along with the predicate, subject type, predicate type and object type.
# Answer:"""
# # # # user_message = "What is 42 * 42?"
# prompt = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant"

# text = create_completion(prompt=prompt, grammar=gbnf_grammar, n_predict=512)
# print(text)



# # Create two prompts and grammars for your API requests

# # prompt1 = """Please analyze the provided context and two entities. Just fill the output fields in the Json format described below and no need for explanation.
# #         JSON_Format: {{'subject': {{output}}, 'object': {{output}}, 'predicate': {{output}}, 'subject_type':{{output}}, 'object_type':{{output}}, 'predicate_type':{{output}} }}
# #         Context: We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca.
# #         Entity 1: deposition and Entity 2: a shale interval
# #         Query: Determine which entity is the subject and which is the object in the context, along with the predicate, subject type, predicate type and object type.
# #         Answer:"""


# # # Create a list of prompts and grammars
# # prompts = [prompt1, prompt]


# # # Create a ThreadPoolExecutor with 2 threads (for 2 simultaneous requests)
# # with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
# #     # Use executor.map to send the requests concurrently
# #     responses = list(executor.map(send_api_request, prompts))

# # # Process the responses
# # for i, response in enumerate(responses):
# #     print(f"Response {i+1}:")
# #     print(json.dumps(response, indent=4))