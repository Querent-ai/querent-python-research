# from neo4j import GraphDatabase
# import matplotlib.pyplot as plt
# import pandas as pd
# import networkx as nx
# from networkx.algorithms.community import greedy_modularity_communities
# import csv
# from itertools import combinations
# import pandas as pd

# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         self.__uri = uri
#         self.__user = user
#         self.__password = password
#         self.__driver = None
#         try:
#             self.__driver = GraphDatabase.driver(self.__uri, auth=(user, password))
#         except Exception as e:
#             print("Failed to create the driver:", e)
        
#     def close(self):
#         if self.__driver is not None:
#             self.__driver.close()
    
#     def extract_knowledge_pairs(self, input_data):
#         knowledge_pairs = []

#         # Extract the 'insights' list from the input data
#         insights = input_data.get('insights', [])

#         # Iterate through each item in the insights list
#         for insight in insights:
#             # Extract the 'knowledge' string
#             knowledge_string = insight.get('knowledge', '')

#             # Split the knowledge string by '-' to separate elements
#             elements = knowledge_string.split('-')

#             # Check if there are at least two elements to form a pair
#             if len(elements) > 1:
#                 knowledge_pairs.append((elements[0], elements[2]))

#         return knowledge_pairs
    
#     def find_paths(self, pairs, max_depth=2):
#         G = nx.MultiDiGraph()
#         for start_node, end_node in pairs:
#             query = f"""
#             MATCH path = (start {{name: $start_node}})-[r*1..{max_depth}]->(end {{name: $end_node}})
#             WITH start, end, path, relationships(path) AS rs
#             WHERE ALL(idx IN RANGE(0, length(path) - 2) WHERE (nodes(path)[idx]).name <> (nodes(path)[idx+1]).name)
#             RETURN start.name AS Start, end.name AS End, 
#                 [n IN nodes(path) | n.name] AS Nodes, 
#                 [r IN rs | type(r)] AS Relationships
#             ORDER BY length(path) ASC
#             """
#             with self.__driver.session() as session:
#                 result = session.run(query, start_node=start_node, end_node=end_node)
#                 unique_paths = {}

#                 for record in result:
#                     nodes = record['Nodes']
#                     relationships = record['Relationships']
#                     # Construct a path representation based on relationships
#                     path_repr = ' --> '.join([f'{nodes[i]} --{relationships[i]}--> ' for i in range(len(nodes) - 1)]) + nodes[-1]
                    
#                     # Check for uniqueness of the path by comparing relationship sequences
#                     if path_repr not in unique_paths:
#                         unique_paths[path_repr] = (nodes, set(relationships))

#                 # Add unique paths to the graph
#                 for path_info in unique_paths.values():
#                     nodes, rel_types = path_info
#                     for i in range(len(nodes) - 1):
#                         # Add each unique relationship type between the nodes as a separate edge
#                         for rel_type in rel_types:
#                             if not G.has_edge(nodes[i], nodes[i + 1], key=rel_type):
#                                 G.add_edge(nodes[i], nodes[i + 1], key=rel_type, label=rel_type)
#         return G
    
    
#     def extract_subject_object_pairs(self, G):
#         unique_pairs = set()
#         for u, v in G.edges():
#             unique_pairs.add((u, v))

#         return list(unique_pairs)



#     def export_graph_to_csv(self, G, filename="graph_output.csv"):
#         """Exports the graph edges and their attributes to a CSV file."""
#         with open(filename, mode='w', newline='') as file:
#             writer = csv.writer(file)
#             # Write the header
#             writer.writerow(['Start Node', 'End Node', 'Relationship Type'])
            
#             # Write data
#             for u, v, data in G.edges(data=True):
#                 writer.writerow([u, v, data.get('label', '')])
                

    

#     def draw_graph(self, G, filename="subgraph.png"):
#         """Draws the directed graph with distinct relationships on different arrows, ensuring labels follow the curves."""
#         plt.figure(figsize=(20, 20))  # Large figure size for clarity
#         pos = nx.spring_layout(G, k=0.5, iterations=50)  # Adjust layout spacing for better visibility

#         nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue', alpha=0.6)
        
#         # Initialize a counter for the edges to manage positioning of parallel edges
#         edge_counts = {}
        
#         for u, v, key in sorted(G.edges(keys=True)):
#             if (u, v) not in edge_counts:
#                 edge_counts[(u, v)] = 0
#             else:
#                 edge_counts[(u, v)] += 1

#             edge_data = G[u][v][key]
#             label = edge_data['label']
#             style = 'dashed' if 'impacts' in label else 'solid'
#             color = 'gray' if 'impacts' in label else 'black'
#             width = 2
            
#             # Applying an offset to the connection style to space out parallel edges
#             offset = 0.3 * edge_counts[(u, v)]  # Incrementally offset each additional edge
#             connectionstyle = f'arc3,rad={offset}'
            
#             # Draw the edge
#             nx.draw_networkx_edges(
#                 G, pos,
#                 edgelist=[(u, v)],
#                 width=width,
#                 edge_color=color,
#                 style=style,
#                 arrowstyle='-|>',
#                 connectionstyle=connectionstyle
#             )
            
#             # Calculate the midpoint of the edge for label placement
#             mid_x = (pos[u][0] + pos[v][0]) / 2
#             mid_y = (pos[u][1] + pos[v][1]) / 2

#             # Adjust the label position slightly along the arc
#             label_x = mid_x + offset * 20
#             label_y = mid_y + offset * 20
            
#             # Place label along the edge curve
#             plt.text(label_x, label_y, label, fontsize=9, color='red', ha='center', va='center', 
#                     bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.5'))

#         nx.draw_networkx_labels(G, pos, font_size=12)
#         plt.axis('off')
#         plt.savefig(filename)

#     def export_paths_to_excel(self, G, pairs, filename="paths_output.xlsx"):
#         paths_data = []

#         # Debug: print information about the graph
#         print("Nodes in graph:", G.nodes())
#         print("Edges in graph:", G.edges(data=True))

#         for pair in pairs:
#             print("Pairs---", pair)
#             start = pair[0]
#             end = pair[-1]
#             all_paths = Neo4jConnection.find_simple_paths(G, start, end)
#             for path in all_paths:
#                 relationships = []
#                 for idx in range(len(path) - 1):
#                     u, v = path[idx], path[idx + 1]
#                     if G.has_edge(u, v):
#                         labels = G[u][v]
#                         relationship = ', '.join(label_data['label'] for label_data in labels.values()) if labels else ''
#                         print("--------------------", G[u][v])
#                         print(f"Edge between {u} and {v}: {relationship}")
#                         relationships.append(relationship)
#                     else:
#                         relationships.append('')
#                 path_with_relationships = [f"{u} --> {v} ({rel})" for u, v, rel in zip(path[:-1], path[1:], relationships)]
#                 paths_data.append({
#                     "Node Pair": " --> ".join(pair),
#                     "Path": " --> ".join(path_with_relationships)
#                 })

#         paths_df = pd.DataFrame(paths_data)
#         paths_df.drop_duplicates(inplace=True)
#         paths_df.to_excel(filename, index=False)


#     def find_simple_paths(G, start, end, path=[]):
#         """Find all paths from start to end node in the graph, avoiding cycles."""
#         path = path + [start]
#         # Debug: Print current path exploration
#         print(f"Exploring path: {path}")
#         if start == end:
#             print(f"Reached end: {end}")
#             return [path]
#         if start not in G:
#             print(f"Start node {start} not in graph")
#             return []
#         paths = []
#         for node in G[start]:
#             if node not in path:  # Avoid revisiting nodes already in the path
#                 if start == 'gas_injection' and node == 'eagle_ford_shale_cores':
#                     print(f"From 'gas_injection' to 'eagle_ford_shale_cores' via {node}")
#                 new_paths = Neo4jConnection.find_simple_paths(G, node, end, path)
#                 paths.extend(new_paths)
#         return paths
    
#     def find_directional_intersection(self, pairs1, pairs2):
#         set1 = set(pairs1)
#         set2 = set(pairs2)
#         intersection = set1.intersection(set2)
        
#         return list(intersection)

    
#     def detect_communities(self):
#         """Detects communities within the graph using the Louvain method."""
#         query = """
#         MATCH (n)-[r]->(m)
#         RETURN n.name AS Node, m.name AS ConnectedNode
#         """
#         with self.__driver.session() as session:
#             result = session.run(query)
#             G = nx.Graph()
#             for record in result:
#                 G.add_edge(record['Node'], record['ConnectedNode'])
            
#             communities = list(greedy_modularity_communities(G))
#             return communities
     

# # Configuration for Neo4j
# neo4j_uri = "bolt://localhost:7687"  # Change this to your Neo4j instance
# neo4j_user = "neo4j"  # Change to your Neo4j username
# neo4j_password = "password_neo" 

# # Initialize Neo4j connection
# neo4j_conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
# input_data_1 = {
#   "session_id": "7531ee14532c4ba380bbe619396429c8",
#   "query": "How does the geological variation within the Eagle Ford Shale affect the production outcomes of different wells?",
#   "insights": [
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "carbonate-has_image-hydraulic_fracturing",
#       "sentence": "4.1 geology the shale formation of eagle ford is of the late cretaceous era, roughly 90 million years old. it has a high carbonate content, up to 70%, which makes it brittle and facilitates hydraulic fracturing (texas rrc, 2014). during the cretaceous time the tectonic movements caused the land masses in the south-east, in the direction of the mexican gulf, to be pressed down.",
#       "tags": "carbonate, hydraulic fracturing, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": "underground slope of the geological layers in texas. the depth of the eagle ford shale varies from the surface to more than 4 km underground. source: eagleford.org (2014)",
#       "tags": "depth, eagle ford shale, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": " \n\nt\n\neagle ford shale play, wo\nwestern gulf basin, :\n~~ south texas __.... inal\n\n   \n \n  \n  \n \n\nmies\na sara\ndeg 2\n\nmap dato 'may 29, 2010\n\n \n  \n\n \n\n  \n \n  \n\n \n\neagle ford producing wells (hpd)\n+ ot\n+ cas\neagle ford petroleum windows (ptrohawk, eos, d})\non\nwot gastcondonsate\nry gas\ntop eagle ford subsea depth structure, ft(petrohawk)\neagle ford shale ticknass,ft(eog)\niii one for sat: ausin chak outeropstnris)\n\n   \n\n \n\n \n\n   \n\n \n\n   \n\n \n\f",
#       "tags": "depth, eagle ford shale, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "permeability-has_image-porosity",
#       "sentence": "the wells are located in two counties in different parts of the eagle ford region and there is big chance other parameters than the api gravity differ between the counties. such parameters could be permeability, porosity, brittleness (ability to induce fractures) and other geological parameters. if the porosity is higher more water will be used in the hydro-fracturing and more of fracturing water would stay in the reservoir.",
#       "tags": "permeability, porosity, has image"
#     }
#   ]
# }

# input_data_2 = {
#   "session_id": "7531ee14532c4ba380bbe619396429c8",
#   "query": "How does the carbonate content affect hydaulic fracturing techniques ?",
#   "insights": [
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-affects-carbonate",
#       "sentence": "the combined data thus de- fine a single overall trend, the slope of which becomes steeper with decreasing porosity on the semilog coor- dinates used (figure 7). ehrenberg and nadeau (2005) presented a global compilation of the average porosity and permeability values for carbonate reservoirs. trends of porosity ver-",
#       "tags": "porosity, carbonate, affects"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "temperature-controls-porosity",
#       "sentence": "bashari, a., 2005, khuff formation permian-triassic carbonate in the qatar-south fars arch hydrocarbon province of the persian gulf: first break, v. 23, p. 43-50. bjorkum, p. a., and p. h. nadeau, 1998, temperature controlled porosity/permeability reduction, fluid migration, and petroleum exploration in sedimentary basins: australian petroleum pro- duction and exploration association journal, v. 38, p. 453-465. bos, c. f. m., 1989, planning an appraisal/development program for the complex khuff carbonate reservoir in the yibal field, north oman: society of petroleum engineers paper 17988, proceedings of the spe 6th middle east oil show, p. 631-640.",
#       "tags": "temperature, porosity, controls"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-is_examined_for-khuff_or_arab_reservoirs",
#       "sentence": "two main aspects of these results are innovative. this is the first time that porosity and permeability values for either khuff or arab reservoirs have been examined regionally. second, the conclusion that ther- mal exposure is the primary control on average poros- ity and permeability in these units is consistent with previous work from other carbonates, but is new for the middle east.",
#       "tags": "porosity, khuff or arab reservoirs, is examined for"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "thermal_exposure-is_the_primary_control_on-average_porosity_and_permeability",
#       "sentence": "second, the conclusion that ther- mal exposure is the primary control on average poros- ity and permeability in these units is consistent with previous work from other carbonates, but is new for the middle east. introduction carbonate reservoirs from producing oil and gas fields have extreme ranges of porosity and permeability, both locally within a single reservoir zone and in terms of average values for entire reservoir zones (ehrenberg and nadeau, 2005). this study describes the latter type of variation for two major reservoir formations in the middle east and lists the factors that seem likely to account for the striking overall differences between these units.",
#       "tags": "thermal exposure, average porosity and permeability, is the primary control on"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "pressure-has_image-temperature",
#       "sentence": "as the name indicates, the compounds consist mainly of hydrogen and carbon. their composition as well as the pressure and temperature determine whether the hydrocarbons occur as liquid or gas (satter et al., 2008). in the first subsection of this chapter (2.1) it is described how the hydrocarbons were formed and some important geological concepts are explained.",
#       "tags": "pressure, temperature, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "hydraulic_fracturing-has_image-permeability",
#       "sentence": "source: u.s. energy information administration (2012). 3.2.2 hydraulic fracturing hydraulic fracturing increases the permeability of tight reservoirs by creating new fractures in the rock. the technology simply means that a mix of water, sand and chemicals are pumped down the wellbore into the target rock where the pressure creates new cracks in the rock and the sand keep the new fractures open.",
#       "tags": "hydraulic fracturing, permeability, has image"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "carbonate-affects-porosity",
#       "sentence": "saner, s., and a. sahin, 1999, lithological and zonal porosity- permeability distributions in the arab-d reservoir, uthma- niyah field, saudi arabia: aapg bulletin, v. 83, no. 2, p. 230- 243. schmoker, j. w., 1984, empirical relation between carbonate po- rosity and thermal maturity: an approach to regional porosity prediction: aapg bulletin, v. 68, p. 1697-1703. sharland, p. r., r. archer, d. m. casey, r. b. davies, s. h. hall, a. p. heward, a. d. horbury, and m. d. simmons, 2001, arabian plate sequence stratigraphy: geoarabia special publi- cation 2, 371 p.",
#       "tags": "carbonate, porosity, affects"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "permeability-is_a_property_of-carbonate",
#       "sentence": "alsharhan, a. s., and k. magara, 1994, the jurassic of the arabian basin: facies, depositional setting and hydrocarbon habitat, in a. f. embry, ed., pangea: global environments and resources: canadian society of petroleum geologists memoir 17, p. 397- 412. alsharhan, a. s., and k. magara, 1995, nature and distribution of porosity and permeability in jurassic carbonate reservoirs of the arabian gulf basin: facies, v. 32, p. 237-254. alsharhan, a. s., and a. e. m. nairn, 1994, the late permian car- bonates (khuff formation) in the western arabian gulf:",
#       "tags": "permeability, carbonate, is a property of"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "burial_depth-controls-porosity",
#       "sentence": "far as average permeability also correlates with porosity (figure 7), it may be concluded that burial depth, by controlling porosity, is also a major factor responsible for the lower average permeabilities of khuff as com- pared with arab reservoirs. despite the overriding importance of thermal expo- sure, as reflected in the top-reservoir-depth parameter, several other well-known differences between khuff and arab carbonates have tended to reinforce the temperature- driven contrasts in reservoir quality. one of these fac- tors is the different platform geometries characterizing the two units.",
#       "tags": "burial depth, porosity, controls"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "khuff-has_greater_burial_diagenesis_than-arab",
#       "sentence": "table 1. factors accounting for differences in average porosity and permeability between khuff and arab reservoirs factors khuff arab burial diagenesis more chemical compaction and associated cementation caused by greater thermal exposure shallower burial depths correspond to greater preservation of primary porosity depositional setting extensive, poorly circulated, very low-relief shelf well-circulated conditions nearer to margins facing deep intracratonic basins dominant lithologies grainstones having relatively fine grain size and mudstones grainstones and grain-dominated packstones primary mineralogy aragonite mainly calcite anhydrite cement extensive anhydrite plugging of entire zones localized anhydrite cementation dolomite major proportion of reservoirs, finely crystalline minor to moderate proportion of reservoirs, medium to coarsely crystalline dominant pore types moldic and intercrystalline primary intergranular, intrafossil, and microporosity petroleum phase gas oil ehrenberg et al. 281figure 8.",
#       "tags": "khuff, arab, has greater burial diagenesis than"
#     }
#   ]
# }


# input_data_3 = {
#   "session_id": "7531ee14532c4ba380bbe619396429c8",
#   "query": "In the Eagle Ford Shale, what other geological parameters have impact on well productivity ?",
#   "insights": [
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "carbonate-has_image-hydraulic_fracturing",
#       "sentence": "4.1 geology the shale formation of eagle ford is of the late cretaceous era, roughly 90 million years old. it has a high carbonate content, up to 70%, which makes it brittle and facilitates hydraulic fracturing (texas rrc, 2014). during the cretaceous time the tectonic movements caused the land masses in the south-east, in the direction of the mexican gulf, to be pressed down.",
#       "tags": "carbonate, hydraulic fracturing, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": "underground slope of the geological layers in texas. the depth of the eagle ford shale varies from the surface to more than 4 km underground. source: eagleford.org (2014)",
#       "tags": "depth, eagle ford shale, has image"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "depth-has_image-eagle_ford_shale",
#       "sentence": " \n\nt\n\neagle ford shale play, wo\nwestern gulf basin, :\n~~ south texas __.... inal\n\n   \n \n  \n  \n \n\nmies\na sara\ndeg 2\n\nmap dato 'may 29, 2010\n\n \n  \n\n \n\n  \n \n  \n\n \n\neagle ford producing wells (hpd)\n+ ot\n+ cas\neagle ford petroleum windows (ptrohawk, eos, d})\non\nwot gastcondonsate\nry gas\ntop eagle ford subsea depth structure, ft(petrohawk)\neagle ford shale ticknass,ft(eog)\niii one for sat: ausin chak outeropstnris)\n\n   \n\n \n\n \n\n   \n\n \n\n   \n\n \n\f",
#       "tags": "depth, eagle ford shale, has image"
#     },
#     {
#       "document": "Asphaltene Precipitation and Deposition during Nitrogen Gas Cyclic Miscible and Immiscible Injection in Eagle Ford Shale and Its Impact on Oil Recovery (2).pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "gas_injection-conducted_for-eagle_ford_shale_cores",
#       "sentence": "in this part of the experiment, eight eagle ford shale cores were used to conduct cyclic gas injection experiments to investigate the efect of miscible and immiscible conditions for n2 on oil recovery and asphaltene deposition. an additional four saturated cores were not exposed to gas injection and served as references (constants) to determine the wettability and pore size distribution before conducting the cyclic experiments. the efects of soaking time, production time, and injection pressure were analyzed.",
#       "tags": "gas injection, eagle ford shale cores, conducted for"
#     },
#     {
#       "document": "Asphaltene Precipitation and Deposition during Nitrogen Gas Cyclic Miscible and Immiscible Injection in Eagle Ford Shale and Its Impact on Oil Recovery (2).pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-affects-permeability",
#       "sentence": "as shown in figure 2, core samples from eagle ford shale outcrops were used in the gas cyclic experiments, with diameter and length of 1 and 2 in, respectively. the average helium porosity was 5.7%, and the average permeability was 198 nd (0.000198 md). x-ray difraction (xrd) analysis of the cores is presented in table 3.",
#       "tags": "porosity, permeability, affects"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "permeability-has_image-porosity",
#       "sentence": "the wells are located in two counties in different parts of the eagle ford region and there is big chance other parameters than the api gravity differ between the counties. such parameters could be permeability, porosity, brittleness (ability to induce fractures) and other geological parameters. if the porosity is higher more water will be used in the hydro-fracturing and more of fracturing water would stay in the reservoir.",
#       "tags": "permeability, porosity, has image"
#     }
#   ]
# }

# input_data_4 = {
#   "session_id": "7531ee14532c4ba380bbe619396429c8",
#   "query": "How do variations in the geological depth and carbonate content influence the choice and effectiveness of hydraulic fracturing techniques ?",
#   "insights": [
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "hydraulic_fracturing-has_image-permeability",
#       "sentence": "source: u.s. energy information administration (2012). 3.2.2 hydraulic fracturing hydraulic fracturing increases the permeability of tight reservoirs by creating new fractures in the rock. the technology simply means that a mix of water, sand and chemicals are pumped down the wellbore into the target rock where the pressure creates new cracks in the rock and the sand keep the new fractures open.",
#       "tags": "hydraulic fracturing, permeability, has image"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-affects-carbonate",
#       "sentence": "the combined data thus de- fine a single overall trend, the slope of which becomes steeper with decreasing porosity on the semilog coor- dinates used (figure 7). ehrenberg and nadeau (2005) presented a global compilation of the average porosity and permeability values for carbonate reservoirs. trends of porosity ver-",
#       "tags": "porosity, carbonate, affects"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "carbonate-is_the_primary_control_on_average_porosity_and_permeability_in_these_units-permeability",
#       "sentence": "second, the conclusion that ther- mal exposure is the primary control on average poros- ity and permeability in these units is consistent with previous work from other carbonates, but is new for the middle east. introduction carbonate reservoirs from producing oil and gas fields have extreme ranges of porosity and permeability, both locally within a single reservoir zone and in terms of average values for entire reservoir zones (ehrenberg and nadeau, 2005). this study describes the latter type of variation for two major reservoir formations in the middle east and lists the factors that seem likely to account for the striking overall differences between these units.",
#       "tags": "carbonate, permeability, is the primary control on average porosity and permeability in these units"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "temperature-controls-porosity",
#       "sentence": "bashari, a., 2005, khuff formation permian-triassic carbonate in the qatar-south fars arch hydrocarbon province of the persian gulf: first break, v. 23, p. 43-50. bjorkum, p. a., and p. h. nadeau, 1998, temperature controlled porosity/permeability reduction, fluid migration, and petroleum exploration in sedimentary basins: australian petroleum pro- duction and exploration association journal, v. 38, p. 453-465. bos, c. f. m., 1989, planning an appraisal/development program for the complex khuff carbonate reservoir in the yibal field, north oman: society of petroleum engineers paper 17988, proceedings of the spe 6th middle east oil show, p. 631-640.",
#       "tags": "temperature, porosity, controls"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "horizontal_drilling-has_image-hydraulic_fracturing",
#       "sentence": "since the beginning of this century the shale oil production has increased from practically zero to currently supply almost half of the u.s. oil production. this development is made possible by the technology of horizontal drilling and hydraulic fracturing. since the production has not been ongoing for that long, production data is still fairly limited in length and there are still large uncertainties in many parameters, for instance production decline, lifespan, drainage area, geographical extent and future technological development.",
#       "tags": "horizontal drilling, hydraulic fracturing, has image"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "permeability-is_a_property_of-carbonate",
#       "sentence": "alsharhan, a. s., and k. magara, 1994, the jurassic of the arabian basin: facies, depositional setting and hydrocarbon habitat, in a. f. embry, ed., pangea: global environments and resources: canadian society of petroleum geologists memoir 17, p. 397- 412. alsharhan, a. s., and k. magara, 1995, nature and distribution of porosity and permeability in jurassic carbonate reservoirs of the arabian gulf basin: facies, v. 32, p. 237-254. alsharhan, a. s., and a. e. m. nairn, 1994, the late permian car- bonates (khuff formation) in the western arabian gulf:",
#       "tags": "permeability, carbonate, is a property of"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-is_examined_for-khuff_or_arab_reservoirs",
#       "sentence": "two main aspects of these results are innovative. this is the first time that porosity and permeability values for either khuff or arab reservoirs have been examined regionally. second, the conclusion that ther- mal exposure is the primary control on average poros- ity and permeability in these units is consistent with previous work from other carbonates, but is new for the middle east.",
#       "tags": "porosity, khuff or arab reservoirs, is examined for"
#     },
#     {
#       "document": "Ghawar Field, Saudi Arabia_A comparison of Khuff and Arab reservoir potential throughout the Middle East.pdf",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-is_influenced_by-depth",
#       "sentence": "ehrenberg, s. n., and p. h. nadeau, 2005, sandstone versus car- bonate petroleum reservoirs: a global perspective on porosity- depth and porosity-permeability relationships: aapg bulletin, v. 89, p. 435-445. focke, j. w., and d. munn, 1985, cementation exponents (m) in middle eastern carbonate reservoirs: society of petroleum en- gineers paper 13735, proceedings of the spe 8th middle east oil show, p. 431-437.",
#       "tags": "porosity, depth, is influenced by"
#     },
#     {
#       "document": "Decline curve analysis of shale oil production_ The case of Eagle Ford.docx",
#       "source": "azure://testfiles/",
#       "knowledge": "porosity-has_image-permeability",
#       "sentence": "this is the rock's ability to transmit fluids. the porosity and the permeability are somewhat correlated but a high porosity does not necessarily mean that the permeability is also high. for the permeability to be good the pores need to be interconnected and large enough not to inhibit the flow of fluids.",
#       "tags": "porosity, permeability, has image"
#     }
#   ]
# }

# pairs_1 = neo4j_conn.extract_knowledge_pairs(input_data_1)
# pairs_2 = neo4j_conn.extract_knowledge_pairs(input_data_2)
# pairs_3 = neo4j_conn.extract_knowledge_pairs(input_data_3)
# pairs_4 = neo4j_conn.extract_knowledge_pairs(input_data_4)

# #### Scenario 1
# print("--------------------Pairs 1 --------", pairs_1)

# graph = neo4j_conn.find_paths(pairs_1)

# neo4j_conn.draw_graph(graph, "pair1.png")

# neo4j_conn.export_graph_to_csv(graph, filename="pair1.csv")
# neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_1, filename="pair1.xlsx")


# # print("-------------------------Pairs 2---------------", pairs_2)
# # graph = neo4j_conn.find_paths(pairs_2)

# # neo4j_conn.draw_graph(graph, "pair2.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair2.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_2, filename="pair2.xlsx")


# # print("-------------------------Pairs 3---------------", pairs_3)

# # graph = neo4j_conn.find_paths(pairs_3)

# # neo4j_conn.draw_graph(graph, "pair3.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair3.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_3, filename="pair3.xlsx")

# # print("-------------------------Pairs 4---------------", pairs_4)
# # graph = neo4j_conn.find_paths(pairs_4)

# # neo4j_conn.draw_graph(graph, "pair4.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair4.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_4, filename="pair4.xlsx")



# #### Scenario 2
# print("--------------------Pairs 1 --------", pairs_1)

# graph = neo4j_conn.find_paths(pairs_1)

# pairs_1 = neo4j_conn.extract_subject_object_pairs(graph)
# print("--------------------Pairs 1 --------", pairs_1)
# # neo4j_conn.draw_graph(graph, "pair1.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair1.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_1, filename="pair1.xlsx")


# print("-------------------------Pairs 2---------------", pairs_2)
# graph = neo4j_conn.find_paths(pairs_2)

# pairs_2 = neo4j_conn.extract_subject_object_pairs(graph)
# print("--------------------Pairs 2 --------", pairs_2)

# # neo4j_conn.draw_graph(graph, "pair2.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair2.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_2, filename="pair2.xlsx")


# print("-------------------------Pairs 3---------------", pairs_3)

# graph = neo4j_conn.find_paths(pairs_3)

# pairs_3 = neo4j_conn.extract_subject_object_pairs(graph)
# print("--------------------Pairs 3 --------", pairs_3)

# # neo4j_conn.draw_graph(graph, "pair3.png")

# # neo4j_conn.export_graph_to_csv(graph, filename="pair3.csv")
# # neo4j_conn.export_paths_to_excel(G=graph, pairs= pairs_3, filename="pair3.xlsx")

# print("-------------------------Pairs 4---------------", pairs_4)
# graph = neo4j_conn.find_paths(pairs_4)

# pairs_4 = neo4j_conn.extract_subject_object_pairs(graph)
# print("--------------------Pairs 4 --------", pairs_4)


# intersection_pairs = neo4j_conn.find_directional_intersection(pairs_1, pairs_2)
# print("Intersection 1 -------------", intersection_pairs)
# graph = neo4j_conn.find_paths(intersection_pairs)

# intersection_pairs = neo4j_conn.extract_subject_object_pairs(graph)


# intersection_pairs = neo4j_conn.find_directional_intersection(intersection_pairs, pairs_3)
# print("Intersection 2 -------------", intersection_pairs)
# graph = neo4j_conn.find_paths(intersection_pairs)

# intersection_pairs = neo4j_conn.extract_subject_object_pairs(graph)

# intersection_pairs = neo4j_conn.find_directional_intersection(intersection_pairs, pairs_4)
# print("Intersection 3 -------------", intersection_pairs)

# graph = neo4j_conn.find_paths(intersection_pairs)

# neo4j_conn.draw_graph(graph, "final.png")

# neo4j_conn.export_graph_to_csv(graph, filename="final.csv")
# print("Graph -----", graph)
# neo4j_conn.export_paths_to_excel(G=graph, pairs= intersection_pairs, filename="final.xlsx")


# # communities = neo4j_conn.detect_communities()
# # print("Detected communities:", communities)

# neo4j_conn.close()
