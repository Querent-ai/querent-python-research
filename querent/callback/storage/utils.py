from querent.storage.storage_base import Storage

def add_prefix_to_storage(storage: Storage, prefix: str, uri: Uri) -> Storage:
    return PrefixStorage(storage, prefix, uri)