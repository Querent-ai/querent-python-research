# Relationship Extraction Algorithm (LLAMA2)<br />

## Example Input for Relationship Extraction:<br /><br />

```python
[
  ('tectonic', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.11, "pair_attnscore": 0.15, "entity1_embedding": [3.9851672649383545, 5.444354057312012, 12.452054023742676, 0.40023085474967957, 5.477858543395996, -3.328960418701172, 7.499555587768555, -0.6432888507843018, 0.176153764128685, 4.574844837188721], "entity2_embedding": [3.910417318344116, 4.3172736167907715, 10.927567481994629, -0.4440983533859253, 5.645864009857178, -3.3608360290527344, 6.031068325042725, -0.13075894117355347, 1.19158935546875, 4.028927803039551], "sentence_embedding": [10.228797912597656, 0.9078602194786072, 3.8210675716400146, 2.9826271533966064, -1.7877899408340454, 9.019113540649414, 7.322807788848877, 0.4493107795715332, 5.830756187438965, 5.221020698547363]}', 'upstream'),
 ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [3.031496524810791, 5.5543012619018555, 12.802851676940918, -0.40406331419944763, 5.433542251586914, -4.073908805847168, 7.429781436920166, -0.35669469833374023, 1.03021240234375, 5.3818559646606445], "entity2_embedding": [3.7557637691497803, 4.355807781219482, 10.816529273986816, -0.5670130848884583, 5.616918087005615, -3.3334271907806396, 5.912326335906982, -0.06841135025024414, 1.1116150617599487, 4.205568790435791], "sentence_embedding": [9.40550708770752, 1.8712570667266846, 4.63387393951416, 3.8367974758148193, -1.094395637512207, 8.434747695922852, 6.475388050079346, 1.6503015756607056, 5.695371150970459, 5.418364524841309]}', 'upstream'), 
  ('deposition', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [3.6060078144073486, 6.190525531768799, 12.511820793151855, 0.2952989339828491, 5.2114458084106445, -3.542228937149048, 7.520601272583008, -0.6833171844482422, 0.31914183497428894, 4.374380588531494], "entity2_embedding": [3.9278876781463623, 4.369570255279541, 10.83134651184082, -0.3810097873210907, 5.6381611824035645, -3.3257150650024414, 6.1031060218811035, -0.1740904599428177, 0.879339873790741, 3.5072436332702637], "sentence_embedding": [9.471346855163574, 1.8663707971572876, 4.568644046783447, 3.7678043842315674, -0.9877296090126038, 8.311663627624512, 6.345090389251709, 1.6819571256637573, 5.708926677703857, 5.485371112823486]}', 'upstream')
]
``` 
<br><br />

## Trigger for the Relationship Extraction to start work:

Event Type : NER_GRAPH_UPDATE
We have subscribed the relationship extractor class to NER_GRAPH_UPDATE event type emitted from the bert llm class.  When this event type signal is emitted, the handle_event function is triggered inside the relationship extractor which is responsible for extracting relationships. Below is the workflow of the relationship extractor:
<br /><br />

### I. Data Validation in RealtionExtractor:<br />

The validate method in the RealtionExtractor class serves as a crucial data validation mechanism. It first checks whether the provided data is non-empty 
and structured as a list, logging an error and returning False if these conditions are not met. The method then iterates through the first item in the list,
ensuring they are tuples (triplets) with the first and third elements as strings. If the item fails these checks, the method logs a specific error 
message and returns False, thereby ensuring the data adheres to the expected format before further processing.

<br /><br />

### II. Predicate-Context Normalization:<br /><br />

Utilizes the TextNormalizer class to normalize each triple. This includes:
1. Lowercasing the text.<br />
2. Lemmatizing each token (word) in the text.<br />
3. Removing stop words from the text.<br />
4. Each triple's context is processed through these normalization steps.<br />

<br />
Output Example
<br />

```python
[('tectonic', '{"context": "study , present evidence paleocene\\u2013eocene thermal maximum ( petm ) record within 543-m-thick ( 1780 ft ) deep-marine section gulf mexico ( gom ) using organic carbon stable isotope biostratigraphic constraint . suggest climate tectonic perturbation upstream north american catchment induce substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition shale interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly thick sedimentary section deep-sea fan gom basin .", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.11, "pair_attnscore": 0.15, "entity1_embedding": [4.785828113555908, 4.2147417068481445, 4.608402729034424, 7.86382532119751, -3.119875907897949, 6.4056620597839355, 4.736032962799072, 0.40054139494895935, -1.7422124147415161, 9.150322914123535], "entity2_embedding": [4.749422073364258, 3.777057647705078, 6.303576946258545, 8.151358604431152, -2.55820369720459, 5.3259968757629395, 6.484385967254639, 0.4279687702655792, -0.9084129333496094, 7.9470624923706055], "sentence_embedding": [-0.4015790522098541, 3.746861696243286, 6.176400661468506, 5.342568397521973, -0.9461199641227722, -6.17316198348999, -4.8703389167785645, 13.388699531555176, 8.222224235534668, 14.191060066223145]}', 'upstream')]
```

<br />

### III. Trim Triples<br />
1. Each input triple is expected to be in the form (entity1, predicate, entity2). The predicate is a JSON string that contains multiple key-value pairs related to the entities.<br />
2. Within each triple, the function parses the predicate and selectively extracts key fields like 'normalized_context', 'entity1_nn_chunk', 'entity2_nn_chunk', 'entity1_label', and 'entity2_label'. It discards any other information present in the predicate.<br />
3. For each original triple, a new triple is constructed. This new triple maintains the original entities (entity1 and entity2) but replaces the original predicate with a trimmed version containing only the extracted fields.<br />
4. The function compiles these restructured triples into a list, effectively creating a streamlined version of the original data, which is then returned for further use in the processing pipeline.<br />

```python
[('tectonic', {'context': 'study , present evidence paleocene–eocene thermal maximum ( petm ) record within 543-m-thick ( 1780 ft ) deep-marine section gulf 
mexico ( gom ) using organic carbon stable isotope biostratigraphic constraint . suggest climate tectonic perturbation upstream north american catchment induce 
substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition shale 
interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly thick 
sedimentary section deep-sea fan gom basin .', 'entity1_nn_chunk': 'tectonic perturbations', 'entity2_nn_chunk': 'the upstream North American catchments', 
'entity1_label': 'B-GeoPetro', 'entity2_label': 'B-GeoMeth'}, 'upstream')]
```

<br />

### IV. Create a local index using FAISS vectordb store for now<br />

This is a comprehensive solution for embedding-based text processing and retrieval, leveraging the power of sentence transformers for embeddings and FAISS for efficient similarity searches.

1. The EmbeddingStore class is designed for handling embeddings and indexing them using FAISS (Facebook AI Similarity Search). It initializes with a default model name for embeddings (e.g., 'sentence-transformers/all-MiniLM-L6-v2') and a path for storing the vector index.<br />
2. Utilizes the HuggingFaceEmbeddings module to generate embeddings based on the specified model. These embeddings are used for creating FAISS indices.<br />
3. The create_index method processes input texts and creates a FAISS index. This method employs a SentenceTransformersTokenTextSplitter for splitting texts into manageable chunks based on token count.<br />
4. It tokenizes and chunks each input text, ensuring that each chunk does not exceed a predefined token limit (e.g., 250 tokens).<br />
5. Once the texts are split into chunks, it converts these chunks into Document objects and then uses these documents to create a FAISS index.<br />
6. The class provides functionality to save the created FAISS index to a file (save_index) and to load an existing index from a file (load_index), facilitating persistence and retrieval of indexed data.<br />
7. The as_retriever method allows for retrieving documents from the index based on similarity or other search criteria, making it a powerful tool for information retrieval tasks using the pre-computed embeddings.<br />
<br />
![](https://github.com/Querent-ai/querent-ai/blob/nishant/docs/images/Local_faiss_index.png)


### V. Extract Relationships<br />


1. The method iterates through each triple, comprising entity1, entity2, and predicate_str. It checks if predicate_str is a dictionary; if not, it parses predicate_str from JSON format.<br />
2. Implements a method ask_question to handle custom question-answering. It checks if search parameters have changed and updates the retriever accordingly.
Retrieves relevant documents based on the input prompt and reorders them for context relevance.
3. For each triple, the method formulates a validation question to ascertain if entity1 and entity2 have a relationship. This question is sent to a question-answering system (self.qa_system). If the answer suggests a relationship exists (contains "yes"), the method then asks a second question to determine the nature of the relationship.
4. Utilizes a custom chain (custom_stuff_chain) to process the reordered documents with the input query and the template, generating the final output (relationships).
5. The method updates the triples with relationship information.


```python
[('tectonic', '{"context": "study , present evidence paleocene\\u2013eocene thermal maximum ( petm ) record within 543-m-thick ( 1780 ft ) deep-marine section 
gulf mexico ( gom ) using organic carbon stable isotope biostratigraphic constraint . suggest climate tectonic perturbation upstream north american catchment 
induce substantial response downstream sector gulf coastal plain ultimately gom . relationship illustrated deep-water basin ( 1 ) high accom- modation deposition 
shale interval coarse-grained terrigenous material wa trapped upstream onset petm , ( 2 ) considerable increase sedi- ment supply petm , archived particularly 
thick sedimentary section deep-sea fan gom basin .", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", 
"entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "relationship": "1. Tectonic perturbation upstream North American catchment may have induced a 
substantial response downstream in the Gulf Coastal Plain, ultimately affecting the GOM deep-water basin.\\n            2. The increase in sediment supply during 
the PETM may have been archived in particularly thick sedimentary sections of the deep-sea fan in the GOM basin."}', 'upstream'),]
```