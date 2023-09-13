
# Entity Extraction Doc

## Context and Scope
Entity extraction, often termed as Named Entity Recognition (NER), is a pivotal task in the realm of Natural Language Processing (NLP). In the context of our project, the goal is to harness the power of advanced language models and tools to perform entity extraction and document-level coreference resolution on large volumes of data.

Entity extraction along with coreference resolution are pivotal in enhancing the understanding and processing of large textual datasets. These techniques enable us to identify, classify, and link entities, ensuring that the context and relationships within the text are preserved and understood.

In this document, I will introduce the workflow of our entity extraction system, which leverages data from cloud storage and employs advanced language models and tools for processing. The key components and actions of this system include:

- Data Retrieval

- Document-Level Coreference Resolution

- Extract Entities

By the end of this document, you will have a comprehensive understanding of our entity extraction system, its components, and its capabilities in processing and understanding vast textual datasets.
## Proposal
Our proposal presents a comprehensive system designed to handle data from diverse sources and extract entities with high accuracy. By integrating state-of-the-art tools and strategies, we aim to create a pipeline that not only extracts entities but also understands the context and relationships within the text. This foundation will be instrumental in our future endeavors, especially in constructing and analyzing entity relationship graphs.
Here's a breakdown of our proposed system:

### Data Collection

### Entity Extraction Pipeline
- [Co-reference Resolution](#coreference)
- [Entity Extraction](#entityextraction)


 **Co-reference Resolution** <a id='coreference'></a>

 ![](https://github.com/Querent-ai/querent-ai/blob/nishant/docs/images/coref-1.gif)
    (copyright: https://explosion.ai/blog/coref)

1. **Using spaCy with NeuralCoref for Co-refererence resolution:**

NeuralCoref is an extension for spaCy's named entity recognition system, adding the capability of neural network-based coreference resolution. In essence, it identifies mentions in a text that refer to the same entity, such as linking the pronoun "she" to a previously mentioned "Jane Doe".
When integrated with spaCy, NeuralCoref leverages spaCy's tokenization and dependency parsing capabilities, while adding its own neural models to resolve coreferences. This combined approach ensures that the context around entities is preserved and understood.

Here's a brief workflow of using spaCy with NeuralCoref for co-reference resolution:

- Initialization: Load spaCy's language model and add the NeuralCoref component to the pipeline.
- Tokenization and Parsing: Process the input text using spaCy's tokenizer and parser, creating a Doc object with tokens and their linguistic features.
- Coreference Resolution: NeuralCoref identifies coreferent mentions in the Doc, linking them together. For instance, in the sentence "Jane is a data scientist. She works at TechCorp.", NeuralCoref will recognize that "She" refers to "Jane".

            

#### Spacy NeuralCoref Usage:

```python

# Import the necessary libraries
import spacy
import neuralcoref

# Initialize the standard English model from SpaCy
spacy_model = spacy.load('en_core_web_sm')

# Integrate the neuralcoref with the loaded SpaCy model
neuralcoref.add_to_pipe(spacy_model)

# Process a complex sample text using the enhanced SpaCy model
sample_text = u"John, who works at TechCorp, bought a new car. He said it's more fuel-efficient than his old one. Meanwhile, TechCorp is planning to provide electric charging stations for its employees."
processed_text = spacy_model(sample_text)

# Check for coreference presence and retrieve coreference clusters
has_coreference = processed_text._.has_coref
coreference_groups = processed_text._.coref_clusters

```


2. **Using AllenNLP for Co-refererence resolution:**

AllenNLP, a product of the Allen Institute for AI, is a notable open-source library in the field of Natural Language Processing, built atop the PyTorch platform. A significant strength of AllenNLP lies in its ability to handle coreference resolution. This task, essentially about identifying words or phrases in text that reference the same entity, is crucial for a clear and contextual understanding of any narrative. By leveraging deep learning models, AllenNLP efficiently maps related mentions within a document, providing a nuanced understanding of the text. For those in the research community and developers aiming for precision, AllenNLP serves as a reliable tool, adept at connecting pronouns to their antecedents or discerning when different terms in a document refer to the same entity.


```python

# Import the necessary libraries
from allennlp.predictors.predictor import Predictor
import allennlp_models.coref

# Load the coreference resolution model
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/coref-spanbert-large-2021.03.10.tar.gz")


# Input text
text = "Eva and Martha didn't want their friend Jenny to feel lonely so they invited her to the party in Las Vegas."

# Get coreference resolution
predictions = predictor.predict(document=text)

# Print the resolved text
resolved_text = predictions['document']
for cluster in predictions['clusters']:
    mention = cluster[0]
    referent = cluster[-1]
    resolved_text[mention[0]:mention[1]+1] = [resolved_text[referent[0]]]
    for idx in range(mention[0]+1, mention[1]+1):
        resolved_text[idx] = ""

print(' '.join(resolved_text))

"Eva and Martha didn't want Eva and Martha's friend Jenny to feel lonely so Eva and Martha invited their friend Jenny to the party in Las Vegas."
```
3. **Using BERT for Co-refererence resolution:**

BERT (Bidirectional Encoder Representations from Transformers) is a transformer-based model that has revolutionized the field of Natural Language Processing (NLP) due to its ability to capture deep contextual information from text. Its bidirectional nature allows it to understand the context of each word based on all its surrounding words, making it particularly powerful for tasks that require understanding relationships between different parts of a text.

- Contextual Embeddings: Coreference resolution inherently requires understanding the context in which words or phrases appear. BERT's strength lies in generating embeddings that are deeply contextual, making it well-suited for identifying whether two mentions refer to the same entity.

- Transfer Learning: BERT is pre-trained on a massive corpus, enabling it to understand a wide range of linguistic constructs. This pre-trained knowledge can be fine-tuned on a smaller, task-specific dataset for coreference resolution, allowing us to leverage BERT's general linguistic knowledge while tailoring it to the nuances of coreference.

- End-to-End Training: Traditional coreference resolution systems often involve multiple stages, including mention detection, mention-pair classification, and clustering. With BERT, there's potential to design end-to-end models that handle all these stages in a unified manner, simplifying the pipeline and potentially improving performance.

- Challenges: While BERT holds promise, it's essential to note that coreference resolution is a complex task. The model needs to handle various challenges, such as:

    a. Distinguishing between pronouns and their potential antecedents.

    b. Understanding long-range dependencies where the referring expression and  its antecedent are far apart.

    c. Handling nested and overlapping mentions.

```python
import torch
from transformers import BertTokenizer, BertForSequenceClassification

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)  # 2 labels: coreferent or not

# Fine-tuning on coreference data (pseudo-code)
# for sentence, mention1, mention2, label in coreference_dataset:
#     inputs = tokenizer(mention1 + " [SEP] " + mention2, return_tensors="pt")
#     outputs = model(**inputs, labels=label)
#     loss = outputs.loss
#     loss.backward()
#     optimizer.step()

# Sample sentence with two mentions
sentence = "John is a software engineer. He works at Google."
mention1 = "John"
mention2 = "He"

# Check if the two mentions are coreferent using the fine-tuned BERT model
inputs = tokenizer(mention1 + " [SEP] " + mention2, return_tensors="pt")
outputs = model(**inputs)
predicted_label = torch.argmax(outputs.logits, dim=1).item()

if predicted_label == 1:
    print(f"'{mention1}' and '{mention2}' are coreferent.")
else:
    print(f"'{mention1}' and '{mention2}' are not coreferent.")
```

This code provides a basic structure for using BERT for coreference resolution. In practice, you'd need a labeled coreference dataset to fine-tune the BERT model, and you'd likely want to incorporate additional steps like mention detection and clustering of coreferent mentions.
## Comparison and Limitations
Here's a sample from the dataset that delves into the historical background of hot dogs.

Henceforth, we'll refer to the NeuralCoref implementation by Huggingface as "Huggingface" and the solution offered by the Allen Institute as "AllenNLP".

 ![](https://github.com/Querent-ai/querent-ai/blob/nishant/docs/images/Original%20vs%20Spacy%20vs%20AllenNLP.png)
    (copyright: https://neurosys.com/blog/popular-frameworks-coreference-resolution#article-3)

- ***Anaphora vs. Cataphora: Understanding Referential Expressions***

    In linguistics, when we discuss the relationships between different parts of a text, two terms often come up: anaphora and cataphora. Both are forms of endophora, where a word or phrase in a sentence refers to another part of the same text. However, the direction of this reference is what differentiates the two.

    - **Anaphora:**
    An anaphoric reference occurs when a word or phrase refers back to another word or phrase that has already been mentioned in the discourse. It's like looking back in the text to find its antecedent.


    - **Cataphora:**
    
    Conversely, a cataphoric reference is when a word or phrase refers forward to another word or phrase that will be mentioned later in the discourse. It's like giving a teaser before revealing the full information.

```
    Example:

    "Even though he was late, John made sure to apologize to every guest."
    Here, "he" is a cataphoric reference, as it points forward to "John," which appears later in the sentence.
```

