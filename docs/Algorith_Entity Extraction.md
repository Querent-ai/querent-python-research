# NER-LLM Extraction Algorithm (BERT)<br />

## Example Text:

"In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints."<br /><br />

## 1. NER-LLM-Transfomer:

The code waits for the entire text of the document to come through  and then passes it through the below algorithm :<br /><br />

### I. _tokenize_and_chunk (output below -> tokenized_sentence, original_sentence, sentence_idx)<br />

```python

Output : [(['in', 'this', 'study', ',', 'we', 'present', 'evidence', 'of', 'a', 'paleocene', '–', 'eocene', 'thermal', 'maximum', '(', 'pet', '##m', ')', 'record', 'within', 'a', '54', '##3', '-', 'm', '-', 'thick', '(', '17', '##80', 'ft', ')', 'deep', '-', 'marine', 'section', 'in', 'the', 'gulf', 'of', 'mexico', '(', 'gom', ')', 'using', 'organic', 'carbon', 'stable', 'isotopes', 'and', 'bio', '##stratigraph', '##ic', 'constraints', '.'], 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 0)] 

```
<br /><br />

### II. We iterate over the above output and produce binary entity pairs using the following:<br /><br />

#### a.) We use the tokenized represtation of a sentence to aggregate chunks (## happens due to the wordpiece tokenizer of BERT). This step is to ensure that in one go we only send a string of max 512 tokens to BERT which is its maximum size. It also takes care of the boundary scenarios where a word may just be split at the end of 510 tokens
<br />
Example
<br />

```python
tokens = ["Dummy", "world", "##!", "This", "is", "a", "test", "##ing", "function", "##ality", "."]

max_chunk_size = 5

First chunk: ["Dummy", "world", "##!", "This", "is"]
Second chunk: ["a", "test", "##ing", "function", "##ality"]
Third chunk: ["."]

```
Actual output :

```python
[['in', 'this', 'study', ',', 'we', 'present', 'evidence', 'of', 'a', 'paleocene', '–', 'eocene', 'thermal', 'maximum', '(', 'pet', '##m', ')', 'record', 'within', 'a', '54', '##3', '-', 'm', '-', 'thick', '(', '17', '##80', 'ft', ')', 'deep', '-', 'marine', 'section', 'in', 'the', 'gulf', 'of', 'mexico', '(', 'gom', ')', 'using', 'organic', 'carbon', 'stable', 'isotopes', 'and', 'bio', '##stratigraph', '##ic', 'constraints', '.']]

```

<br />

#### b.) extract entities from each chunk and append them to the output using LLM<br />

```python
[{'entity': 'eocene', 'label': 'B-GeoTime', 'score': 0.9998507499694824, 'start_idx': 11}, {'entity': 'thermal', 'label': 'B-GeoMeth', 'score': 0.9903227686882019, 'start_idx': 12}, {'entity': 'ft', 'label': 'B-GeoMeth', 'score': 0.6936133503913879, 'start_idx': 30}, {'entity': 'mexico', 'label': 'B-GeoLoc', 'score': 0.9209132790565491, 'start_idx': 40}, {'entity': 'organic', 'label': 'B-GeoPetro', 'score': 0.9996106028556824, 'start_idx': 45}, {'entity': 'carbon', 'label': 'B-GeoPetro', 'score': 0.997830331325531, 'start_idx': 46}, {'entity': 'isotopes', 'label': 'B-GeoMeth', 'score': 0.956226646900177, 'start_idx': 48}]

```
<br />

#### c.) Implement Dependency Parsing <br />

performs dependency parsing on a given sentence using the SpaCy library. <br />

1. extract noun chunks from the sentence<br />
2. filter noun chunks to ensure their root word is a noun and not a stop word<br />
3. we merge the overlapping noun chunks into single chunks<br />
4. we then compare individual entities with the noun chunks and check for their presence in noun_chunks<br />
5. we finally group entities by their associated noun chunks and then process these grouped entities to generate a final list of entities<br />
        a. If there's only one entity associated with a noun chunk:<br />
              - we round the score of the entity to two decimal places.<br />
              - set default values for 'noun_chunk' and 'noun_chunk_length'<br />
              - appends the entity to the processed_entities list.<br /><br />
        b. If there are multiple entities associated with a noun chunk, it:<br />
              - computes the set of unique labels from the entities.<br />
              - calculates the average score of the entities.<br />
              - constructs a new processed_entity dictionary with combined information from the grouped entities.<br />
              - append the processed_entity to the processed_entities list.<br /><br />
```python
[    {'entity': 'red', 'label': 'color', 'score': 0.9, 'noun_chunk': 'red apple', 'start_idx': 1},    {'entity': 'apple', 'label': 'fruit', 'score': 0.8, 'noun_chunk': 'red apple', 'start_idx': 1}]


[    {'entity': 'red', 'label': 'color, fruit', 'score': 0.85, 'noun_chunk': 'red apple', 'noun_chunk_length': 2, 'start_idx': 1}]

```
<br />

Actual output :

```python
[{'entity': 'eocene', 'label': 'B-GeoMeth, B-GeoTime', 'score': 1.0, 'noun_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'noun_chunk_length': 6, 'start_idx': 11}, {'entity': 'ft', 'label': 'B-GeoMeth', 'score': 0.69, 'start_idx': 30, 'noun_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'noun_chunk_length': 6}, {'entity': 'mexico', 'label': 'B-GeoLoc', 'score': 0.92, 'start_idx': 40, 'noun_chunk': 'Mexico', 'noun_chunk_length': 1}, {'entity': 'organic', 'label': 'B-GeoMeth, B-GeoPetro', 'score': 0.98, 'noun_chunk': 'organic carbon stable isotopes', 'noun_chunk_length': 4, 'start_idx': 45}]
```
<br />

#### d.) Now that we have individual entities identified, now is the time to start finding binary entity pairs. Below is the algorith:<br />
1. if 2 entities lie next to each other without any words or tokens in between them, it is rejected as a binary entity pair<br />
2. 2 entities should be from the same sentence<br />
3. the maximum distance between 2 entities after remoiving stop words should be less than 10 (changeable) tokens<br />
4. if all the above criterias are fullfilled, we create an entity pair<br />
5. finally we format these entity pairs into desirable format <br />

<br />

output :

```python
[[
    ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section'}), 


    ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico'})

]]
```
<br />

### Add attention weights to the entity pairs

1. we want to know how much attention the model pays to the entities "eocene" and "ft" in the sentence.<br />
2. we find the sentence containing both entities. If no such sentence is found, the full context is used.<br />
3. tokenize the sentence and forward pass through the model to get attention outputs<br />
4. the entity is also tokenized to find the corresponding token IDs that the model uses to represent the entity.<br />
5. the positions of these entity tokens within the input sequence are identified<br />
6. collect all non-zero attention weights<br />
   a. for each attention head in the last layer of the model, the attention weights corresponding to the entity token positions are collected.<br />
   b. only non-zero attention weights are considered. This is because zero attention weights indicate no attention being paid to those tokens, and including them would not contribute to understanding the model's focus on the entity <br />
   c. the non-zero attention weights are then used to calculate a weighted mean. This is done by squaring the attention weights (to give more weight to higher attention scores) and summing them up.<br />
   d. this sum is then divided by the sum of the non-zero attention weights to normalize it<br />
   e. the result is a single scalar value that represents the weighted mean attention that the model pays to the entity token<br />
   f. If there are no non-zero attention weights (highly unusual), the function returns an attention weight of 0, indicating no attention paid to the
   entity<br />

7. advantage of this approach:<br />
  a. focus on Relevant Weights:by considering only non-zero attention weights, the algorithm focuses on parts of the model's attention that are actually active.This avoids diluting the attention measure with zeros, which would otherwise lower the average attention score. Remember different heads focus on differs parts of the input sentence<br />
  b. emphasis on Stronger Signals:squaring the attention weights before calculating the mean gives more importance to higher attention scores. This is based on the assumption that higher attention weights are more significant and should therefore have a greater impact on the final score.<br />
  c. normalization:dividing by the sum of the non-zero attention weights normalizes the weighted mean, ensuring that the result is not skewed by the number of non-zero weights. <br />

8. Potential Limitations:<br />
  a. last Layer Focus:the algorithm only considers the attention weights from the last layer of the transformer model. While the last layer is often the most relevant for many tasks, earlier layers can also provide valuable insights, especially in multi-layer transformers where lower layers capture different aspects of the input.<br />
  b. head Averaging: the algorithm averages across all heads, which might mask the fact that different heads can learn to attend to different types of  information.<br />
  c. squaring Weights:squaring the attention weights before averaging them is a design choice but could overemphasize outliers.<br />

9. Extract a combined attention score for the binary pair using harmonic mean to penalize entity pairs where one entity has a much lower score than the other<br />
 


```python
[[
   ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'entity1_attnscore': 0.2, 'entity2_attnscore': 0.09, 'pair_attnscore': 0.12}), 
   ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico', 'entity1_attnscore': 0.2, 'entity2_attnscore': 0.09, 'pair_attnscore': 0.13})
]]

```
<br />

### Add contextual embeddings to the entity pairs<br />
1. returns the contextual embedding vector for the entity in the given context<br />
2. the context is the sentence in which the entity is found<br />
3. the embedding vector of the entity could be of a very large dimension like 768, 1024 so we need to apply the dimensionality reduction UMAP<br />
4. we first extract the embeddings of all the entity pairs and then use these embeddings to fit the UMAP model<br />
5. we then pass the entity embedding vector to reduce its dimensions to 10 (changeable but tested and works well)<br />
6. we also compute the embedding vector of the sentence in which the entities are present and reduce it to 10 dimesnions<br />
6. finally append these embedding vectors to their respective entity pairs <br />



```python


[[
      ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'entity1_attnscore': 0.2, 'entity2_attnscore': 0.09, 'pair_attnscore': 0.12, 'entity1_embedding': array([11.036303 ,  2.8076973,  8.389541 ,  3.2040212,  3.4598484,
         7.0396004,  3.9861436,  4.116618 ,  8.681216 ,  8.636501 ],
         dtype=float32), 'entity2_embedding': array([9.715959 , 2.203084 , 8.864678 , 3.470288 , 3.6868083, 7.5623245,
         5.529193 , 3.3847048, 7.9975386, 8.562227 ], dtype=float32), 'sentence_embedding': array([-0.54448974,  7.5149374 ,  8.517842  , -2.1653118 ,  7.0120473 ,
         4.347338  ,  4.953186  ,  6.298759  ,  1.9099524 ,  9.259526  ],
         dtype=float32)}), 
      ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico', 'entity1_attnscore': 0.2, 'entity2_attnscore': 0.09, 'pair_attnscore': 0.13, 'entity1_embedding': array([11.027176 ,  2.712821 ,  8.322338 ,  3.264398 ,  3.40767  ,
        7.263025 ,  4.190097 ,  4.3689775,  8.675622 ,  8.491512 ],
      dtype=float32), 'entity2_embedding': array([10.902329 ,  2.345167 ,  9.295886 ,  2.8256547,  3.8414454,
        6.883073 ,  4.45736  ,  3.436294 ,  8.722808 ,  8.973055 ],
      dtype=float32), 'sentence_embedding': array([-0.10598744,  7.32935   ,  8.490395  , -2.1447139 ,  7.0116305 ,
        4.3481045 ,  4.954007  ,  6.2976675 ,  2.0612082 ,  9.053885  ],
      dtype=float32)})
      
]]

```

<br />

### 2. Convert the above output into the format (subject: str, predicate: str, object: str) pairs <br />
1. it accepts a nested list of tuples named data and a file_path string as inputs.<br />
2. extends the tuple with the file_path in which the entity pairs were found in.<br />
3. converts the extended tuple to a ContextualPredicate object and then to a JSON string.<br />


```python
[
   ('eocene', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.", "entity1_score": 1.0, "entity2_score": 0.69, "entity1_label": "B-GeoTime, B-GeoMeth", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "a Paleocene\\u2013Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "a 543-m-thick (1780 ft) deep-marine section", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.2, "entity2_attnscore": 0.09, "pair_attnscore": 0.12, "entity1_embedding": [8.732972145080566, -3.0359280109405518, 6.889065742492676, 3.376582145690918, 3.0003528594970703, 13.417505264282227, 2.4588003158569336, 2.8393120765686035, 5.30462121963501, 2.8973538875579834], "entity2_embedding": [8.034997940063477, -3.2363924980163574, 7.317476749420166, 4.331025123596191, 1.9272148609161377, 13.824652671813965, 1.6136497259140015, 3.7104339599609375, 5.758291721343994, 3.401808261871338], "sentence_embedding": [15.984325408935547, 15.321417808532715, 14.980063438415527, 10.209357261657715, 6.230877876281738, 9.16944694519043, 6.558372497558594, 6.729509353637695, 7.912111282348633, 1.1400314569473267]}', 'ft'), 
   ('eocene', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM.", "entity1_score": 1.0, "entity2_score": 0.92, "entity1_label": "B-GeoTime, B-GeoMeth", "entity2_label": "B-GeoLoc", "entity1_nn_chunk": "a Paleocene\\u2013Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "Mexico", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.2, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [8.69924545288086, -2.979280471801758, 6.972227096557617, 3.501229763031006, 3.0274736881256104, 13.416812896728516, 2.4797191619873047, 2.8480584621429443, 5.319562911987305, 3.032069444656372], "entity2_embedding": [8.64617919921875, -4.001160144805908, 6.817051410675049, 3.2022833824157715, 1.746004343032837, 13.622705459594727, 1.8317079544067383, 3.2205424308776855, 4.623369216918945, 3.7013437747955322], "sentence_embedding": [15.925633430480957, 15.26292610168457, 14.921666145324707, 10.1509428024292, 6.217123508453369, 9.1832914352417, 6.5722455978393555, 6.715585231781006, 7.898133754730225, 1.311438798904419]}', 'mexico')
]
```
<br />

### 3. Filtering entity pairs<br />
1.  expects triples in the form of (entity1, context, entity2), where 'context' is a JSON string containing various attributes including the embeddings<br />
2.  calculate the cosine similarity between two entity embeddings and filters triples by checking if the cosine similarity between entity embeddings meets the 
similarity threshold.<br />
3.  filters triples by checking if the entity scores meet the score threshold.<br />
4.  filters triples by checking if the pair attention score meets the attention score threshold.<br />
5.  combine_embeddings(entity1_embedding, entity2_embedding) and then clusters the filtered triples from step 4 by using the HDBSCAN algorithm on combined
 embeddings and returns the clusters removing the noise<br />
6. user can configure the following parameter for hbdscan : score_threshold, attention_score_threshold, similarity_threshold, min_cluster_size, min_samples<br />
7. user can even turn on/off the filtering step<br />


<br />

### 4. Convert the extracted triples above to contextualknowledge triples (subject: URI, predicate: BNODE, object: URI) pairs<br />
1. subject string ('entity1') is concatenated was a base uri('http://geodata.org') and converted to a URI -> ('http://geodata.org/entity1')<br />
2. object string ('entity2') is concatenated was a base uri('http://geodata.org') and converted to a URI -> ('http://geodata.org/entity2')<br />
3. predicate, represented as a dictionary with key-value pairs, is transformed into a BNode (a blank node) using its string representation.<br />
4. distinct list of subjects is generated, to which objects and predicates are appended as attributes.<br />
5. these step produces contextual knwoledge triplets for the entire document<br />
6. finally we raise an event type of Token Processed with payload as the triplest produced above.<br />


```python
[
    (<querent.graph.utils.URI object at 0x7fe912d1bd00>, <querent.graph.utils.BNode object at 0x7fe96017bc40>, <querent.graph.utils.URI object at 0x7fe9a46527d0>),
    (<querent.graph.utils.URI object at 0x7fe912d613f0>, <querent.graph.utils.BNode object at 0x7fe912d63880>, <querent.graph.utils.URI object at 0x7fe912d60ca0>)
    
]
```