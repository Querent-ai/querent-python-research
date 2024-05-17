from __future__ import annotations
import sys
from pathlib import Path
import logging
import numpy as np
from gguf import GGUFReader, GGUFValueType
import json

class GGUFMetadataExtractor:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.reader = GGUFReader(self.model_path, 'r')
        self.model_arch_value = None

    def get_file_host_endian(self) -> tuple[str, str]:
        host_endian = 'LITTLE' if np.uint32(1) == np.uint32(1).newbyteorder("<") else 'BIG'
        file_endian = 'BIG' if self.reader.byte_order == 'S' else host_endian
        return (host_endian, file_endian)

    def dump_metadata(self) -> None:
        params = []
        for n, field in enumerate(self.reader.fields.values(), 1):
            pretty_type = self.format_field_type(field)
            log_message = f'  {n:5}: {pretty_type:10} | {len(field.data):8} | {field.name}'
            if len(field.types) == 1:
                curr_type = field.types[0]
                if curr_type == GGUFValueType.STRING:
                    log_message += ' = {0}'.format(repr(str(bytes(field.parts[-1]), encoding='utf-8')[:60]))
                elif curr_type in self.reader.gguf_scalar_to_np:
                    log_message += ' = {0}'.format(field.parts[-1][0])
                params.append(log_message)
        return params
    
    def format_field_type(self, field) -> str:
        if not field.types:
            return 'N/A'
        if field.types[0] == GGUFValueType.ARRAY:
            nest_count = len(field.types) - 1
            return '[' * nest_count + str(field.types[-1].name) + ']' * nest_count
        return str(field.types[-1].name)

    def dump_metadata_json(self) -> None:
        host_endian, file_endian = self.get_file_host_endian()
        metadata, tensors = {}, {}
        result = {
            "filename": self.model_path,
            "endian": file_endian,
            "metadata": metadata,
            "tensors": tensors,
        }
        self.fill_metadata_json(metadata)
        json.dump(result, sys.stdout)

    def fill_metadata_json(self, metadata):
        for idx, field in enumerate(self.reader.fields.values()):
            curr = {
                "index": idx,
                "type": field.types[0].name if field.types else 'UNKNOWN',
                "offset": field.offset,
                "value": self.extract_field_value(field)
            }
            metadata[field.name] = curr

    def extract_field_value(self, field):
        if field.types[:1] == [GGUFValueType.ARRAY]:
            if field.types[-1] == GGUFValueType.STRING:
                return [str(bytes(part, encoding="utf-8")) for part in field.parts]
            return [pv.tolist() for part in field.parts for pv in part]
        if field.types[0] == GGUFValueType.STRING:
            return str(bytes(field.parts[-1], encoding="utf-8"))
        return field.parts[-1].tolist()

    def extract_general_name(self, lines):
        for line in lines:
            if "general.architecture" in line:
                parts = line.split('=')
                if len(parts[1].strip().strip("'")) > 1:
                    return parts[1].strip().strip("'")
        return "Name not found"


# Usage example
# if __name__ == '__main__':
#     extractor = GGUFMetadataExtractor("/home/nishantg/querent-main/querent/tests/llama-2-7b-chat.Q5_K_M.gguf")
#     model_metadata = extractor.dump_metadata()
#     model_name = extractor.extract_general_name(model_metadata)
#     print(model_name)