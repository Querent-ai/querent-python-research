from langchain.prompts import PromptTemplate
from langchain import LLMChain
from langchain.output_parsers import ResponseSchema, StructuredOutputParser

from querent.config.core.relation_config import RelationshipExtractorConfig

class BSMBranch:
    def __init__(self):
        # Initialize the appropriate language model based on the provided model name
        # self.llm_llama = CTransformers(model='./tests/llama-2-7b-chat.Q4_K_M.gguf', config=config, model_type='llama')
        # self.llm_falcon = CTransformers(model='/home/nishantg/Downloads/falcon-7b-instruct.ggccv1.q4_1.bin', config=config, model_type='falcon')
        
        Subject = ResponseSchema(
                        name="subject",
                        description="The subject of a knowledge graph triple.",
                    )
        Predicate = ResponseSchema(
                        name="predicate",
                        description="The predicate of a knowledge graph triple.",
                    )
        Object = ResponseSchema(
                        name="Object",
                        description="The object of a knowledge graph triple.",
                    )
        self.output_parser = StructuredOutputParser.from_response_schemas(
                    [Subject, Predicate, Object]
                )
        self.format_instructions = self.output_parser.get_format_instructions()
        print(self.format_instructions)


    def create_llm_chain(self, llm, template, format_instructions:bool=False):
        if format_instructions:
            llm_chain = LLMChain(prompt=PromptTemplate(template=template, input_variables=["query", "context"], partial_variables={"format_instructions": self.format_instructions}), llm=llm)
        else:
            llm_chain = LLMChain(prompt=PromptTemplate(template=template, input_variables=["query", "context"]), llm=llm)
        #return llm_chain.run({"entity1": entity1,"entity2": entity2, "context": context})
        return llm_chain
    
    def create_sub_tasks(self, tasks, llm, template, model_type, format_instructions:bool=False):
        sub_tasks = []
        for task in tasks:
            model_chain = self.create_llm_chain(llm=llm, template=template, format_instructions=format_instructions)
            sub_tasks.append((model_chain, model_type, task))
        return sub_tasks

# # Example usage
# config = {'max_new_tokens': 100, 'temperature': 0, 'repetition_penalty': 1.7, 'context_length': 2000}
# bsm_branch = BSMBranch(config=config)

# #bsm_branch.add_sub_task("Custom sub-task prompt with {entity1}, {entity2}, and {context}.")

# # Example entities and context
# entity1 = "Python"
# entity2 = "Programming"
# context = "Python is a high-level, interpreted programming language known for its simplicity."

# results = bsm_branch.extract_and_evaluate_relationship(entity1, entity2, context)
# for task, result_llama, result_falcon in results:
#     print(f"Task: {task}\nLLama Result: {result_llama}\nFalcon Result: {result_falcon}\n")


