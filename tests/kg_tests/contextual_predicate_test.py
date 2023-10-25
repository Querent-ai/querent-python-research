import pytest
from querent.kg.contextual_predicate import ContextualPredicate, convert_tuples_to_json
from querent.core.base_engine import BaseEngine
from typing import List, Tuple, Dict

"""
    Test the functionality of the ContextualPredicate class and its associated utility function.

    This test covers the following scenarios:
    1. Conversion of sample data tuples into a JSON format using the `convert_tuples_to_json` utility function.
    2. Verification of the correctness of the conversion against an expected JSON string.

    Assertions:
    - Ensure that the conversion of the sample data to JSON format is accurate and matches the expected JSON string.

"""
    

def test_contextual_predicate():
    sample_data = [
        ('eocene', 'ABSTRACT In this study...', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.99, 'entity1_label': 'B-GeoTime, B-GeoMeth', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico'}),
        ('eocene', 'ABSTRACT In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'organic', {'entity1_score': 1.0, 'entity2_score': 0.98, 'entity1_label': 'B-GeoTime, B-GeoMeth', 'entity2_label': 'B-GeoMeth, B-GeoPetro', 'entity1_nn_chunk': 'Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'organic carbon stable isotopes'}),
    ]
    result_list = convert_tuples_to_json(sample_data)
    result_string = result_list[0] if result_list else ""
    expected_string = '{"context": "ABSTRACT In this study...", "entity1_score": 1.0, "entity2_score": 0.99, "entity1_label": "B-GeoTime, B-GeoMeth", "entity2_label": "B-GeoLoc", "entity1_nn_chunk": "Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "Mexico"}'    
    assert result_string == expected_string, f"Expected {expected_string}, but got {result_string}"

