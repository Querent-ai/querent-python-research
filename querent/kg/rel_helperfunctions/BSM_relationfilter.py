from langchain.prompts import PromptTemplate
from langchain import LLMChain
from pydantic import BaseModel, Field, validator
from typing import List

from querent.config.core.relation_config import RelationshipExtractorConfig


class BSMBranch:
    def create_llm_chain(self, llm, template, format_instructions:bool=False):
        if format_instructions:
            llm_chain = LLMChain(prompt=PromptTemplate(template=template, input_variables=["query", "context"], partial_variables={"format_instructions": self.format_instructions}), llm=llm)
        else:
            llm_chain = LLMChain(prompt=PromptTemplate(template=template, input_variables=["query", "context"]), llm=llm)
        return llm_chain
    
    def create_sub_tasks(self, tasks, llm, template, model_type, format_instructions:bool=False):
        sub_tasks = []
        for task in tasks:
            model_chain = self.create_llm_chain(llm=llm, template=template, format_instructions=format_instructions)
            sub_tasks.append((model_chain, model_type, task))
        return sub_tasks

