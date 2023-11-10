from pydantic import BaseModel, Field

class RelationshipExtractorConfig(BaseModel):
    name: str = "RelationshipExtractor"
    description: str = "An engine for extracting relationships"
    version: str = "0.0.1"
    logger: str = "RelationshipExtractor.engine_config"


