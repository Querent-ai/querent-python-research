# import pandas as pd
# import re

# # Load your data
# file_path = '/media/ansh/New_Volume_1/reservoir-analysis/graph_event.csv'
# data = pd.read_csv(file_path)

# # Dictionary of geologic time categories and their synonyms
# geologic_time_classification = {
#     'Reservoir': 'reservoir',
#     'Pore pressure': 'reservoir_property',
#     'Ground water': 'ground_water',
#     'Carbonate rock': 'rock_type',
#     'Clastic rock': 'rock_type',
#     'Porosity': 'reservoir_property',
#     'Permeability': 'reservoir_property',
#     'Oil saturation': 'reservoir_property',
#     'Water saturation': 'reservoir_property',
#     'Gas saturation': 'reservoir_property',
#     'Depth': 'reservoir_characteristic',
#     'Size': 'reservoir_characteristic',
#     'Temperature': 'reservoir_characteristic',
#     'Pressure': 'reservoir_characteristic',
#     'Oil viscosity': 'reservoir_property',
#     'Gas-oil ratio': 'reservoir_property',
#     'Water cut': 'production_metric',
#     'Recovery factor': 'production_metric',
#     'Enhanced recovery technique': 'recovery_technique',
#     'Horizontal drilling': 'drilling_technique',
#     'Hydraulic fracturing': 'recovery_technique',
#     'Water injection': 'recovery_technique',
#     'Gas injection': 'recovery_technique',
#     'Steam injection': 'recovery_technique',
#     'Seismic activity': 'geological_feature',
#     'Structural deformation': 'geological_feature',
#     'Faulting': 'geological_feature',
#     'Cap rock integrity': 'reservoir_feature',
#     'Compartmentalization': 'reservoir_feature',
#     'Connectivity': 'reservoir_feature',
#     'Production rate': 'production_metric',
#     'Depletion rate': 'production_metric',
#     'Exploration technique': 'exploration_method',
#     'Drilling technique': 'drilling_method',
#     'Completion technique': 'completion_method',
#     'Environmental impact': 'environmental_aspect',
#     'Regulatory compliance': 'regulatory_aspect',
#     'Economic analysis': 'economic_aspect',
#     'Market analysis': 'economic_aspect'
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
# cleaned_file_path = '/media/ansh/New_Volume_1/reservoir-analysis/cleaned_graph_event.csv'
# data.to_csv(cleaned_file_path, index=False)

# print(f"Data cleaning complete. The cleaned data has been saved to: {cleaned_file_path}")
