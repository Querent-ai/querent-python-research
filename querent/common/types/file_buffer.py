from functools import lru_cache

class FileBuffer:
    """
    A buffer to manage and store file content in chunks using an LRU cache.

    The class is designed to handle file content that comes in chunks. It uses an LRU cache
    to store these chunks efficiently. When a new file starts (indicated by a change in filename),
    the content of the previous file is processed and cleared from the cache.

    Attributes:
        current_filename (str): The name of the file currently being processed.
        _cache (functools._lru_cache_wrapper): The LRU cache storing file content chunks.

    Methods:
        _get_file_content(filename: str) -> list:
            A private method to initialize an empty list for a given filename in the cache.

        add_chunk(filename: str, chunk: str) -> None:
            Add a chunk of data to the buffer for the current file. If a new file starts,
            process the end of the previous file.

        end_file() -> str:
            Process the end of the current file, clear its content from the cache, and return
            the full content of the file.

        get_content(filename: str) -> str:
            Retrieve the full content for a given filename from the cache.
    """

    # Neeed to discuss maxsize with sir
    def __init__(self, maxsize=1000):
        self.current_filename = None
        self._cache = lru_cache(maxsize, typed=False)(self._get_file_content)

    def _get_file_content(self, filename):

        return []

    def add_chunk(self, filename, chunk):
        try:
                if self.current_filename and self.current_filename != filename:
                    return self.end_file()

                self.current_filename = filename
                content = self._cache(filename)
                content.append(chunk)
        except Exception as e:
            self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Unable to add data to cache. {e}"
                )
            raise Exception(f"An error occurred while adding a chunk: {e}")   
             

    def end_file(self):
        try:
            full_content = ''.join(self._cache(self.current_filename))
            self._cache.cache_clear()
            return full_content
        except Exception as e:
            self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Unable to end file cache. {e}"
                )
            raise Exception(f"An error occurred while ending the file: {e}")

    def get_content(self, filename):
        try:
            return ''.join(self._cache(filename))
        except Exception as e:
            self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Unable to get contents from cache. {e}"
                )
            raise Exception(f"An error occurred while getting content for {filename}: {e}")