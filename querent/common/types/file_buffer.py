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
    def __init__(self, maxsize=10000):
        self.current_filename = None
        self._cache = lru_cache(maxsize)(self._get_file_content)

    def _get_file_content(self, filename):
        """Private method to be used by the LRU cache."""
        return []

    def add_chunk(self, filename, chunk):
        """Add a chunk of data to the buffer for a given filename."""

        if self.current_filename and self.current_filename != filename:

            return self.end_file()  # Process the end of the previous file        
        self.current_filename = filename
        content = self._cache(filename)
        content.append(chunk)

    def end_file(self):
        
        """Process the end of a file and clear its content from the buffer."""
        full_content = ''.join(self._cache(self.current_filename))
        # You can process the full_content here or return it for external processing
        self._cache.cache_clear()  # Clear the cache for the processed file
        print("going to challenge:", full_content)
        return full_content

    def get_content(self, filename):
        """Retrieve the full content for a given filename."""
        return ''.join(self._cache(filename))