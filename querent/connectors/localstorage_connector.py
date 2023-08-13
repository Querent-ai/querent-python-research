import os


class LocalStorageConnector:
    def __init__(self, base_path):
        self.base_path = base_path

    def _get_full_path(self, relative_path):
        return os.path.join(self.base_path, relative_path)

    def list_files(self, directory=''):
        directory_path = self._get_full_path(directory)
        try:
            files = [f for f in os.listdir(directory_path) if os.path.isfile(
                os.path.join(directory_path, f))]
            return files
        except OSError as e:
            print("Error listing files:", e)
            return []

    def read_file(self, file_path):
        full_path = self._get_full_path(file_path)
        try:
            with open(full_path, 'r') as file:
                content = file.read()
                return content
        except (OSError, FileNotFoundError) as e:
            print("Error reading file:", e)
            return None

    def write_file(self, file_path, content):
        full_path = self._get_full_path(file_path)
        try:
            with open(full_path, 'w') as file:
                file.write(content)
            return True
        except OSError as e:
            print("Error writing file:", e)
            return False

    def delete_file(self, file_path):
        full_path = self._get_full_path(file_path)
        try:
            os.remove(full_path)
            return True
        except (OSError, FileNotFoundError) as e:
            print("Error deleting file:", e)
            return False


# Usage
base_path = '/Users/ayushjunjhunwala/querent-local/querent-ai/querent/storage'
local_connector = LocalStorageConnector(base_path)

# List files in a directory
files = local_connector.list_files()
print(files)

# Read a file
content = local_connector.read_file('sample.txt')
print(content)

# Write to a file
success = local_connector.write_file('new_file.txt', 'Hello, world!')
print(success)

# Delete a file
success = local_connector.delete_file('new_file.txt')
print(success)
