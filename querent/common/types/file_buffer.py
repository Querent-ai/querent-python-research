from functools import lru_cache

class FileBuffer:
    def __init__(self, maxsize=10000):
        self.current_filename = None
        self._cache = lru_cache(maxsize)(self._get_file_content)

    def _get_file_content(self, filename):
        """Private method to be used by the LRU cache."""
        return []

    def add_chunk(self, filename, chunk):
        """Add a chunk of data to the buffer for a given filename."""
        print("inside add chunks")
        if self.current_filename and self.current_filename != filename:
            self.end_file()  # Process the end of the previous file
        self.current_filename = filename
        content = self._cache(filename)
        content.append(chunk)

    def end_file(self):
        """Process the end of a file and clear its content from the buffer."""
        full_content = ''.join(self._cache(self.current_filename))
        # You can process the full_content here or return it for external processing
        self._cache.cache_clear()  # Clear the cache for the processed file

    def get_content(self, filename):
        print("inside get content")
        """Retrieve the full content for a given filename."""
        return ''.join(self._cache(filename))