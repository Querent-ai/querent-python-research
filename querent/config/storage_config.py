from enum import Enum
from typing import Optional
from pydantic import BaseModel

class StorageBackend(str, Enum):
    Azure = "azure"
    File = "file"
    Ram = "ram"
    S3 = "s3"

class StorageBackendFlavor(str, Enum):
    DigitalOcean = "digital_ocean"
    Garage = "garage"
    Gcs = "gcs"
    MinIO = "minio"

class StorageConfig(BaseModel):
    backend: StorageBackend
    flavor: Optional[StorageBackendFlavor] = None

    class Config:
        use_enum_values = True

class AzureStorageConfig(BaseModel):
    account_name: str
    # Other Azure-specific config fields

class S3StorageConfig(BaseModel):
    access_key_id: str
    secret_access_key: str
    region: str
    endpoint: str
    force_path_style_access: bool
    disable_multi_object_delete: bool
    disable_multipart_upload: bool
    # Other S3-specific config fields

class FileStorageConfig(BaseModel):
    pass

class RamStorageConfig(BaseModel):
    pass
