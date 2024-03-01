# import pandas as pd
# import re

# # Load your data
# file_path = '/home/nishantg/querent-main/querent/tests/data/llm/cleaned_graph_event (copy).csv'
# data = pd.read_csv(file_path)

# # Dictionary of geologic time categories and their synonyms
# geologic_time_classification = {
#     "shale gas": "hydrocarbon_source",
#     "crude oil": "hydrocarbon",
#     "natural gas": "hydrocarbon",
#     "shale oil": "hydrocarbon",
#     "coalbed methane": "hydrocarbon",
#     "methane": "hydrocarbon",
#     "tar sands": "hydrocarbon",
#     "gas hydrates": "hydrocarbon",
#     "hydrates": "hydrocarbon",
#     "oil": "hydrocarbon",
#     "gas": "hydrocarbon",
#     "structural trap": "trap_type",
#     "stratigraphic trap": "trap_type",
#     "combination trap": "trap_type",
#     "salt trap": "trap_type",
#     "trap": "trap_type",
#     "unconformity trap": "trap_type",
#     "placer deposits": "mineral_deposit",
#     "mineral deposit": "mineral_deposit",
#     "deposits": "mineral_deposit",
#     "vein deposit": "mineral_deposit",
#     "porphyry deposit": "mineral_deposit",
#     "kimberlite pipe": "mineral_deposit",
#     "laterite deposit": "mineral_deposit",
#     "sandstone": "rock_type",
#     "shale": "rock_type",
#     "limestone": "rock_type",
#     "dolomite": "rock_type",
#     "shale": "rock_type",
#     "source rock": "rock_type",
#     "cap rock": "rock_type",
#     "volcanic rock": "rock_type",
#     "basalt": "rock_type",

#     "anticline": "structural_feature",
#     "syncline": "structural_feature",
#     "fault": "structural_feature",
#     "terrane" : "structural_feature",
#     "salt dome": "structural_feature",
#     "dome": "structural_feature",
#     "horst": "structural_feature",
#     "graben": "structural_feature",
    

#     "hydrocarbon migration": "geological_process",
#     "accumulation": "geological_process",
#     "migration": "geological_process",
#     "hydrocarbon accumulation": "geological_process",
#     "geothermal gradient": "geological_process",
#     "sedimentology": "geological_discipline",
#     "paleontology": "geological_discipline",
#     "biostratigraphy": "geological_discipline",
#     "sequence stratigraphy": "geological_discipline",
#     "geophysical survey": "geological_method",
#     "magnetic anomaly": "geophysical_feature",
#     "gravitational anomaly": "geophysical_feature",
#     "petrology": "geological_discipline",
#     "geochemistry": "geological_discipline",
#     "hydrogeology": "geological_discipline",
#     "reef": "stratigraphic_feature",
#     "shoal": "stratigraphic_feature",
#     "deltaic deposits": "stratigraphic_feature",
#     "delta": "stratigraphic_feature",
#     "turbidite": "stratigraphic_feature",
#     "channel sandstone": "stratigraphic_feature",
#     "formation": "stratigraphic_feature",
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
# cleaned_file_path = '/home/nishantg/querent-main/querent/tests/data/llm/cleaned_graph_event1.csv'
# data.to_csv(cleaned_file_path, index=False)

# print(f"Data cleaning complete. The cleaned data has been saved to: {cleaned_file_path}")
