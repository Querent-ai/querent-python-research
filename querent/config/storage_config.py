from enum import Enum
from typing import Optional
from pydantic import BaseModel

class StorageBackend(str, Enum):
    LocalFile = "localfile"
    Redis = "redis"
    
class StorageBackendFlavor(str, Enum):
    DigitalOcean = "do"
    Garage = "garage"
    Gcs = "gcp"
    MinIO = "minio"

class StorageConfig(BaseModel):
    backend: StorageBackend
    flavor: Optional[StorageBackendFlavor] = None

    class Config:
        use_enum_values = True

class LocalFileStorageConfig(BaseModel):
    root_path: str

class RedisStorageConfig(BaseModel):
    host: str
    port: int
    password: Optional[str] = None  
    
class StorageConfigWrapper(BaseModel):
    backend: StorageBackend
    config: Optional[BaseModel] = None

    @classmethod
    def from_storage_config(cls, storage_config: StorageConfig):
        if storage_config.backend == StorageBackend.LocalFile:
            return cls(backend=StorageBackend.LocalFile, config=LocalFileStorageConfig())
        elif storage_config.backend == StorageBackend.Redis:
            raise NotImplementedError("Redis storage configuration is not implemented yet")
        else:
            raise ValueError(f"Unsupported storage backend: {storage_config.backend}")
