from querent.logging.logger import setup_logger

class FileBuffer:
    """
    A buffer to manage and store file content in chunks.

    This class handles file content that comes in chunks by storing these chunks in a dictionary.
    When a chunk with None is received, it is interpreted as the end of the current file,
    and the content of that file is processed.

    Attributes:
        current_filename (str): The name of the file currently being processed.
        file_chunks (dict): A dictionary storing file content chunks.

    Methods:
        add_chunk(filename: str, chunk: str) -> None:
            Add a chunk of data to the buffer for the current file. If chunk is None,
            process the end of the file.

        end_file(filename: str) -> str:
            Process the end of the specified file, clear its content from the dictionary,
            and return the full content of the file.

        get_content(filename: str) -> str:
            Retrieve the full content for a given filename from the dictionary.
    """

    def __init__(self):
        self.logger = setup_logger(__name__, "FileBuffer")
        self.file_chunks = {} 

    def add_chunk(self, filename, chunk):
        try:
            if chunk is None:
                return self.end_file(filename)

            if filename not in self.file_chunks:
                self.file_chunks[filename] = {}

            # Automatically assign a chunk ID
            chunk_id = len(self.file_chunks[filename])
            self.file_chunks[filename][chunk_id] = chunk

            return filename, None
                
        except Exception as e:
            self.logger.error(f"Error adding a chunk: {e}")
            raise Exception(f"An error occurred while adding a chunk: {e}")   

    def end_file(self, filename):
        try:
            # Assemble file content from chunks
            if filename in self.file_chunks:
                chunks = self.file_chunks[filename]
                full_content = ''.join([chunks[i] for i in sorted(chunks.keys())])
                del self.file_chunks[filename]  # Clear the file entry
                return filename, full_content
            else:
                raise Exception(f"No chunks found for file: {filename}")
        except Exception as e:
            self.logger.error(f"Error ending the file: {e}")
            raise Exception(f"An error occurred while ending the file: {e}")

    def get_content(self, filename):
        try:
            if filename in self.file_chunks:
                chunks = self.file_chunks[filename]
                return ''.join([chunks[i] for i in sorted(chunks.keys())])
            else:
                raise Exception(f"No content found for file: {filename}")
        except Exception as e:
            self.logger.error(f"Error getting content for {filename}: {e}")
            raise Exception(f"An error occurred while getting content for {filename}: {e}")
