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
3. tokenize the sentence and pass it through the model to get attention outputs<br />
4. identify the positions of the entity tokens within the context.<br />
5. extracts the maximum attention weight for the entity tokens ('eo', '##cene') -> if ##cene has a higher attention weight we will choose this <br />

```python
    ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.21}), 
    
    ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.17})

```
<br />

### Add contextual embeddings to the entity pairs<br />
1. returns the contextual embedding vector for the entity in the given context<br />
2. the context is the sentence in which the entity is found<br />
3. the embedding vector of the entity could be of a very large dimension like 768, 1024 so we need to apply the dimensionality reduction UMAP<br />
4. we first extract the embeddings of all the entity pairs and then use these embeddings to fit the UMAP model<br />
5. we then pass the entity embedding vector to reduce its dimensions to 10 (changeable but tested and works well)<br />
6. finally append these embedding vectors to their respective entity pairs <br />



```python

[[
    ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'ft', {'entity1_score': 1.0, 'entity2_score': 0.69, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoMeth', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'a 543-m-thick (1780 ft) deep-marine section', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.21, 'entity1_embedding': array([ 9.106539  ,  8.942029  ,  5.9552383 ,  3.512078  , -0.49969953,
        8.430279  ,  6.3425374 ,  5.716455  , 20.659513  ,  0.32374638],
      dtype=float32), 'entity2_embedding': array([ 9.390391  ,  9.446289  ,  6.3524523 ,  4.2195497 , -0.03142916,
        6.4198833 ,  6.814947  ,  4.939228  , 20.682281  , -0.80515945],
      dtype=float32)}), 
      
      ('eocene', 'In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.', 'mexico', {'entity1_score': 1.0, 'entity2_score': 0.92, 'entity1_label': 'B-GeoMeth, B-GeoTime', 'entity2_label': 'B-GeoLoc', 'entity1_nn_chunk': 'a Paleocene–Eocene Thermal Maximum (PETM) record', 'entity2_nn_chunk': 'Mexico', 'entity1_attnscore': 0.46, 'entity2_attnscore': 0.17, 'entity1_embedding': array([ 9.208438  ,  8.4275255 ,  6.836303  ,  5.1063766 , -0.62462395,
        8.021709  ,  6.4630294 ,  5.9802933 , 20.921095  ,  0.4295121 ],
      dtype=float32), 'entity2_embedding': array([ 8.098089  ,  8.504325  ,  4.646329  ,  5.0061107 , -0.49743184,
        6.72934   ,  6.177566  ,  6.106788  , 19.969746  ,  0.9939955 ],
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
    ('eocene', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.", "entity1_score": 1.0, "entity2_score": 0.69, "entity1_label": "B-GeoMeth, B-GeoTime", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "a Paleocene\\u2013Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "a 543-m-thick (1780 ft) deep-marine section", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.46, "entity2_attnscore": 0.21, "entity1_embedding": [9.106538772583008, 8.942028999328613, 5.955238342285156, 3.512078046798706, -0.49969953298568726, 8.430278778076172, 6.3425374031066895, 5.716454982757568, 20.659513473510742, 0.32374638319015503], "entity2_embedding": [9.39039134979248, 9.4462890625, 6.352452278137207, 4.219549655914307, -0.03142916038632393, 6.4198832511901855, 6.814947128295898, 4.939228057861328, 20.682281494140625, -0.8051594495773315]}', 'ft'), 
    ('eocene', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints.", "entity1_score": 1.0, "entity2_score": 0.92, "entity1_label": "B-GeoMeth, B-GeoTime", "entity2_label": "B-GeoLoc", "entity1_nn_chunk": "a Paleocene\\u2013Eocene Thermal Maximum (PETM) record", "entity2_nn_chunk": "Mexico", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.46, "entity2_attnscore": 0.17, "entity1_embedding": [9.2084379196167, 8.427525520324707, 6.836303234100342, 5.106376647949219, -0.6246239542961121, 8.021709442138672, 6.463029384613037, 5.980293273925781, 20.92109489440918, 0.4295121133327484], "entity2_embedding": [8.098089218139648, 8.504324913024902, 4.646328926086426, 5.006110668182373, -0.49743184447288513, 6.729340076446533, 6.177566051483154, 6.106788158416748, 19.969745635986328, 0.9939954876899719]}', 'mexico')
]
```

<br />

### 3. Convert the extracted triples above to contextualknowledge triples (subject: URI, predicate: BNODE, object: URI) pairs<br />
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