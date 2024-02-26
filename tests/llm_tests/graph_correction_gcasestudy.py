# import pandas as pd
# import re

# # Load your data
# file_path = '/home/nishantg/Downloads/graph_event (8).csv'
# data = pd.read_csv(file_path)

# # Dictionary of geologic time categories and their synonyms
# geologic_time_classification = {
#     "phanerozoic": "geologic_eon",
#     "proterozoic": "geologic_eon",
#     "archean": "geologic_eon",
#     "hadean": "geologic_eon",
#     "cenozoic": "geologic_era",
#     "mesozoic": "geologic_era",
#     "paleozoic": "geologic_era",
#     "neoproterozoic": "geologic_era",
#     "mesoproterozoic": "geologic_era",
#     "paleoproterozoic": "geologic_era",
#     "neoarchean": "geologic_era",
#     "mesoarchean": "geologic_era",
#     "paleoarchean": "geologic_era",
#     "eoarchean": "geologic_era",
#     "quaternary": "geologic_period",
#     "neogene": "geologic_period",
#     "paleogene": "geologic_period",
#     "cretaceous": "geologic_period",
#     "jurassic": "geologic_period",
#     "triassic": "geologic_period",
#     "permian": "geologic_period",
#     "carboniferous": "geologic_period",
#     "devonian": "geologic_period",
#     "silurian": "geologic_period",
#     "ordovician": "geologic_period",
#     "cambrian": "geologic_period",
#     "ediacaran": "geologic_period",
#     "cryogenian": "geologic_period",
#     "tonian": "geologic_period",
#     "stenian": "geologic_period",
#     "ectasian": "geologic_period",
#     "calymmian": "geologic_period",
#     "statherian": "geologic_period",
#     "orosirian": "geologic_period",
#     "rhyacian": "geologic_period",
#     "siderian": "geologic_period",
#     "holocene": "geologic_epoch",
#     "pleistocene": "geologic_epoch",
#     "pliocene": "geologic_epoch",
#     "miocene": "geologic_epoch",
#     "oligocene": "geologic_epoch",
#     "eocene": "geologic_epoch",
#     "paleocene": "geologic_epoch",
#     # And so on for all other categories and epochs
# }

# # Function to standardize geologic time
# def standardize_geologic_time(value, classification):
#     # Convert the value to lower case and check if it is in the classification dictionary
#     if isinstance(value,str):
#         value_lower = value.lower()
#         if value_lower in classification:
#             # If the value is found in the dictionary, return the corresponding classification
#             return classification[value_lower]
#         else:
#             # If not found, return the original value
#             return value

# # Apply the function to 'subject_type' and 'object_type'
# data['subject_type'] = data['subject'].apply(standardize_geologic_time, args=(geologic_time_classification,))
# data['object_type'] = data['object'].apply(standardize_geologic_time, args=(geologic_time_classification,))

# # Save the cleaned data
# cleaned_file_path = '/home/nishantg/Downloads/cleaned_graph_event.csv'
# data.to_csv(cleaned_file_path, index=False)

# print(f"Data cleaning complete. The cleaned data has been saved to: {cleaned_file_path}")
