from langchain.prompts import PromptTemplate



class BSMBranch:
    
    def create_sub_tasks(self, tasks, query, context, template, grammar):
        sub_tasks = []
        for task in tasks:
            prompt = (PromptTemplate(template=template, input_variables=["query", "context"])).format(context=context, query=query)
            sub_tasks.append((prompt))
        return sub_tasks

