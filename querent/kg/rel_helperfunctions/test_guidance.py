from llama_cpp.llama import Llama, LlamaGrammar
from guidance import models
from langchain.llms import LlamaCpp

import asyncio
import aiofiles

async def read_grammar_file(file_path):
    async with aiofiles.open(file_path, 'r') as file:
        return await file.read()
# llm = LlamaCpp(
#     model_path="/home/nishantg/querent-main/llama-2-7b-chat.Q5_K_S.gguf",
#     temperature=0.75,
#     max_tokens=2000,
#     verbose=True,  # Verbose is required to pass to the callback manager
#     grammar_path = '/home/nishantg/querent-main/querent/querent/kg/rel_helperfunctions/json.gbnf'
# )
async def main():
    file_path = '/home/nishantg/querent-main/querent/querent/kg/rel_helperfunctions/json.gbnf'

    grammar_text = await read_grammar_file(file_path)
    grammar = LlamaGrammar.from_string(grammar_text)

    llm = Llama(model_path="/home/nishantg/querent-main/llama-2-7b-chat.Q5_K_S.gguf", grammar=grammar, max_tokens=-1, temperature=0)
    # llm = Llama(model_path="/home/nishantg/Downloads/vicuna-13b-v1.5.Q4_K_M.gguf")
    # llama2 = models.LlamaCpp("/home/nishantg/querent-main/llama-2-7b-chat.Q5_K_S.gguf")
    # lm = llm + "Who won the last Kentucky derby and by how much?"
    response = llm("""Use the following context to answer the user's question.
            If you don't know the answer, just say that you don't know, don't try to make up an answer.
            Context: In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.
            Question: I want to define a semantic knowledge graph triple (Subject, Predicate, Object) along with the relationship type. The Subject is Tectonic Perturbations and the Object is upstream North American Catchments.
            Only return the helpful answer below and nothing else.
            Helpful answer:""", grammar=grammar, max_tokens=-1, temperature=0)
    print(response)
    print("going to print result")
    # import json
    # print(json.dumps(json.loads(response['choices'][0]['text']), indent=4))

asyncio.run(main())




# # Your grammar rules as a string
# grammar_rules = """
# root ::= SemanticTriple
# SemanticTriple ::= '{' ws '"subject":' ws string ',' ws '"predicate":' ws string ',' ws '"object":' ws string ',' ws '"predicate_type":' ws PredicateType '}'
# SemanticTriplelist ::= '[]' | '[' ws SemanticTriple (',' ws SemanticTriple)* ']'
# PredicateType ::= '"location based"' | '"causal"' | '"temporal"' | '"comparative"' | '"qualitative"' | '"ownership"' | '"passive voice"'
# string ::= '"' ([^"]*) '"'
# boolean ::= 'true' | 'false'
# ws ::= [ \t\n]*
# number ::= [0-9]+ '.'? [0-9]*
# stringlist ::= '[' ws ']' | '[' ws string (',' ws string)* ws ']'
# numberlist ::= '[' ws ']' | '[' ws number (',' ws number)* ws ']'
# """

# # Assuming you are using a library that can parse from a string
# # Example: Llama Grammar Parser (the actual library might be different)
# # from lla import LlamaGrammar
# grammar = LlamaGrammar.from_string(grammar_rules)

# # Use the grammar object as needed in your system
