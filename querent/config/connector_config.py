from pydantic import BaseModel

class ConnectorBackend(BaseModel):
    LocalFile = "localfile"
    Grpc = "grpc"
    Azure = "azure"
    PostgreSQL = "postgresql"
    Ram = "ram"
    S3 = "s3"
    FileStorage = "filestorage"
    ObjectStorage = "objectstorage"
    Database = "database"