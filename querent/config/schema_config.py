from pydantic import BaseModel


class GraphSchemaConfig(BaseModel):
    """
    Schema config for a knowledge graph object.
    """

    name: str
    schema_content: str
    shacl_content: str
    schema_format: str
    shacl_format: str