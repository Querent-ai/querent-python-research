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
#     if isinstance(value, str):
#         value_lower = value.lower()
#         for key in classification:
#             if key in value_lower:  # Check if the classification key is a substring of the value_lower
#                 print("Value---", value_lower)
#                 print("Class--- ", classification[key])
#                 return classification[key]
#     return None

# # Assuming 'data' is a pandas DataFrame and you have 'subject', 'object', 'subject_type', and 'object_type' columns
# # Apply the function to 'subject' and 'object', and temporarily store the results
# data['temp_subject_type'] = data['subject'].apply(lambda x: standardize_geologic_time(x, geologic_time_classification))
# data['temp_object_type'] = data['object'].apply(lambda x: standardize_geologic_time(x, geologic_time_classification))

# # Update 'subject_type' and 'object_type' only where 'temp_subject_type' and 'temp_object_type' are not None
# data['subject_type'] = data.apply(lambda row: row['temp_subject_type'] if row['temp_subject_type'] is not None else row['subject_type'], axis=1)
# data['object_type'] = data.apply(lambda row: row['temp_object_type'] if row['temp_object_type'] is not None else row['object_type'], axis=1)

# # Drop the temporary columns
# data.drop(['temp_subject_type', 'temp_object_type'], axis=1, inplace=True)

# # Save the cleaned data
# cleaned_file_path = '/home/nishantg/querent-main/querent/tests/data/llm/cleaned_graph_event (copy).csv'
# data.to_csv(cleaned_file_path, index=False)

# # print(f"Data cleaning complete. The cleaned data has been saved to: {cleaned_file_path}")
