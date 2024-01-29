# import numpy as np
# import pytest
# from querent.kg.rel_helperfunctions.contextual_predicate import process_data
# from querent.core.base_engine import BaseEngine
# from typing import List, Tuple, Dict

# """
#     Test the functionality of the ContextualPredicate class and its associated utility function.

#     This test covers the following scenarios:
#     1. Conversion of sample data tuples into a JSON format using the `convert_tuples_to_json` utility function.
#     2. Verification of the correctness of the conversion against an expected JSON string.

#     Assertions:
#     - Ensure that the conversion of the sample data to JSON format is accurate and matches the expected JSON string.

# """
    
# def test_contextual_predicate():
#     sample_data = [[('temperatures', 'The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe.', 'kenn', {'entity1_score': 0.91, 'entity2_score': 0.97, 'entity1_label': 'B-GeoMeth', 'entity2_label': 'B-GeoPetro', 'entity1_nn_chunk': 'temperatures', 'entity2_nn_chunk': 'Kennett', 'entity1_attnscore': 0.86, 'entity2_attnscore': 0.09, 'pair_attnscore': 0.16, 'entity1_embedding': [0.0975915715098381], 'entity2_embedding': [-1.2051959037780762]})]]

#     result_list = process_data(sample_data, "dummy1.pdf")

#     # Check if result_list is a list of tuples with three strings each
#     if result_list and all(isinstance(item, tuple) and len(item) == 3 and all(isinstance(element, str) for element in item) for item in result_list):
#         # If the condition is True, the assertion passes
#         assert True
#     else:
#         # If the condition is False, the assertion fails
#         assert False, "result_list is not a list of tuples like List[Tuple[str, str, str]]"

