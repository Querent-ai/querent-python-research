from langchain.llms import LlamaCpp, CTransformers
from langchain.prompts import PromptTemplate
from langchain import LLMChain

class BSMBranch:
    def __init__(self, config):
        # Initialize the appropriate language model based on the provided model name
        self.llm_llama = CTransformers(model='./tests/llama-2-7b-chat.Q4_K_M.gguf', config=config, model_type='llama')
        self.llm_falcon = CTransformers(model='/home/nishantg/Downloads/falcon-7b-instruct.ggccv1.q4_1.bin', config=config, model_type='falcon')
        self.sub_tasks = []
    
    def add_sub_task(self, task):
        self.sub_tasks.append(task)


    def query_llm(self, llm, prompt, entity1, entity2, context):
        llm_chain = LLMChain(prompt=PromptTemplate(template=prompt, input_variables=["entity1", "entity2", "context"]), llm=llm)
        return llm_chain.run({"entity1": entity1,"entity2": entity2, "context": context})

    def extract_and_evaluate_relationship(self, entity1, entity2, context):
        # Extract relationship
        extraction_prompt = "Given the entities {entity1} and {entity2} in the context: {context}, what is their relationship?"
        relationship = self.query_llm(self.llm_llama, extraction_prompt, entity1, entity2, context)
        print(relationship)
        if not self.sub_tasks:
            self.sub_tasks = [
                "Evaluate if a meaningful relationship exists between {entity1} and {entity2}, given their relationship is {context}.".strip(),
                "Determine the type of relationship (e.g., location-based, person-based) between {entity1} and {entity2}, given their relationship is {context}.".strip(),
                "Check the response for factual accuracy regarding the relationship between {entity1} and {entity2}, given their relationship is {context}.".strip(),
                "Assess alignment with the user's question and relevance regarding the relationship between {entity1} and {entity2}, given their user's question is to extract the relationship.".strip(),
                "Identify any temporal and causal relationships between {entity1} and {entity2}, given the relationship is {context}.".strip()
            ]

        results = []
        for task in self.sub_tasks:
            prompt = task
            result_llama = self.query_llm(self.llm_llama, prompt, entity1, entity2, relationship)
            result_falcon = self.query_llm(self.llm_falcon, prompt, entity1, entity2, relationship)
            results.append((task, result_llama, result_falcon))

        return results

# Example usage
config = {'max_new_tokens': 100, 'temperature': 0, 'repetition_penalty': 1.7, 'context_length': 2000}
bsm_branch = BSMBranch(config=config)

#bsm_branch.add_sub_task("Custom sub-task prompt with {entity1}, {entity2}, and {context}.")

# Example entities and context
entity1 = "Python"
entity2 = "Programming"
context = "Python is a high-level, interpreted programming language known for its simplicity."

results = bsm_branch.extract_and_evaluate_relationship(entity1, entity2, context)
for task, result_llama, result_falcon in results:
    print(f"Task: {task}\nLLama Result: {result_llama}\nFalcon Result: {result_falcon}\n")


