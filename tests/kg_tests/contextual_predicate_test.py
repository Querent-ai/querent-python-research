import numpy as np
import pytest
from querent.kg.contextual_predicate import process_data
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
    sample_data = [[('eocene', 'In this study, we present evidence of a PaleoceneEocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a PaleoceneEocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.21, 'pair_attnscore': 0.13,'entity1_embedding': np.array([ 5.513507  ,  6.14687   ,  0.56821245,  3.7250893 ,  8.519092  ,2.1298776 ,  6.7030797 ,  8.760443  , -2.4095411 , 14.959248  ],dtype=np.float32), 'entity2_embedding': np.array([ 4.3211513,  5.3283153,  1.2105073,  5.3618913,  8.23375  ,2.951651 ,  7.3403625, 10.785665 , -2.5593305, 14.518231 ],
      dtype=np.float32)}), ('eocene', 'In this study, we present evidence of a PaleoceneEocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a PaleoceneEocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.17, 'pair_attnscore': 0.13,'entity1_embedding': np.array([ 5.355203  ,  6.1266084 ,  0.60222036,  3.7390788 ,  8.5242195 ,
        2.1033056 ,  6.6313214 ,  8.70998   , -2.432465  , 15.200483  ],
      dtype=np.float32), 'entity2_embedding': np.array([ 5.601423  ,  6.058842  ,  0.33065754,  6.1470265 ,  8.568694  ,
        3.922125  ,  7.0688643 , 11.551212  , -2.5106885 , 14.04761   ],
      dtype=np.float32)})]]
    
    
    # # Convert numpy arrays to lists
    # for inner_list in sample_data:
    #     for tup in inner_list:
    #         if tup:
    #             tup[3]['entity1_embedding'] = tup[3]['entity1_embedding'].tolist()
    #             tup[3]['entity2_embedding'] = tup[3]['entity2_embedding'].tolist()

    result_list = process_data(sample_data, "dummy1.pdf")
    result_string = result_list[0][1] if result_list else ""
    #print("................",result_string)
    expected_string = '{"context": "In this study, we present evidence of a PaleoceneEocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.", "entity1_score": 1.0, "entity2_score": 0.69, "entity1_label": "B-GeoMeth, B-GeoTime", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "a PaleoceneEocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "a 543-m-thick (1780 ft) deep-marine section", "file_path": "dummy1.pdf", "entity1_attnscore": 0.46, "entity2_attnscore": 0.21, "pair_attnscore": 0.13, "entity1_embedding": [5.513506889343262, 6.146870136260986, 0.5682124495506287, 3.7250893115997314, 8.519091606140137, 2.1298775672912598, 6.703079700469971, 8.760442733764648, -2.409541130065918, 14.959247589111328], "entity2_embedding": [4.321151256561279, 5.328315258026123, 1.2105072736740112, 5.361891269683838, 8.233750343322754, 2.951651096343994, 7.340362548828125, 10.785664558410645, -2.559330463409424, 14.518231391906738]}'
    assert result_string == expected_string, f"Expected {expected_string}, but got {result_string}"
