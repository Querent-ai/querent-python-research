from pydantic import BaseModel


class PromethusAdapterConfig(BaseModel):
    """
    PromethusAdapterConfig is the configuration for the prometheus adapter

    Attributes:
        url (str): The url of the prometheus server
        job_name (str): The job name of the prometheus server
    """

    url: str
    port: int
    job_name: str
    labels: [str]
