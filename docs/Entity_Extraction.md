
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


# **Co-reference Resolution** <a id='coreference'></a>

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

- [] Need to implement and check

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

- [] We cannot resolve this issue 100% but what are the possible ways to reduce these errors? The span of text chosen will become crucial in this case
- [] AllenNLP and NeuroCoref need to be used in a type of intersection strategy (https://github.com/NeuroSYS-pl/coreference-resolution)

    In linguistics, when we discuss the relationships between different parts of a text, two terms often come up: anaphora and cataphora. Both are forms of endophora, where a word or phrase in a sentence refers to another part of the same text. However, the direction of this reference is what differentiates the two.

    - **Anaphora:**
    An anaphoric reference occurs when a word or phrase refers back to another word or phrase that has already been mentioned in the discourse. It's like looking back in the text to find its antecedent.

    - **Cataphora:**
    Conversely, a cataphoric reference is when a word or phrase refers forward to another word or phrase that will be mentioned later in the discourse. It's like giving a teaser before revealing the full information.


```
    Anaphora Example:

    "When John arrived at the party, he was immediately greeted by his friends."
    In this sentence, "he" is an anaphoric reference to "John."


    Cataphora Example:

    "Even though he was late, John made sure to apologize to every guest."
    Here, "he" is a cataphoric reference, as it points forward to "John," which appears later in the sentence.
```


-  **NeuralCoref (Huggingface) vs. AllenNLP: Pros and Cons**

| Feature/Aspect       | NeuralCoref (Huggingface)                  | AllenNLP                               |
|----------------------|--------------------------------------------|----------------------------------------|
| **Integration**      | - Easily integrates with spaCy.            | - Standalone library with comprehensive NLP tools. |
|                      | - Can be combined with other spaCy components. | - Requires separate setup from other NLP tools. |
| **Model Architecture** | - Uses a neural network-based approach.  | - Offers deep learning models, often with more architectural variations. |
| **Flexibility**      | - More suited for general-purpose coreference tasks. | - Highly customizable for specific research or advanced tasks. |
| **Performance**      | - Fast and efficient for most standard use cases. | - Might be more computationally intensive but potentially more accurate for complex texts. |
| **Community Support**| - Backed by Huggingface, a well-known entity in NLP. | - Supported by the Allen Institute, renowned for research contributions. |
| **Documentation**    | - Good documentation, but primarily through Huggingface and spaCy channels. | - Extensive documentation with examples, making it research-friendly. |
| **Cons**             | - Might not handle extremely complex coreferences as effectively as dedicated systems. | - Steeper learning curve for those unfamiliar with its ecosystem. |

# **Entity Extraction** <a id='entityextraction'></a>
-[] Need to try Llama2 as well. Although tried asking it for relationships and it was able to spit it out (including entities) but can add a entity extraction specific example
-[] get LLama2 fine-tuning code from debanjan

## Entity Extraction using spaCy

Named Entity Recognition (NER) is a pivotal task in NLP, aiming to identify and categorize named entities within text, such as persons, organizations, and dates. One of the prominent libraries in the NLP realm, spaCy, offers a streamlined and potent solution for this.

### How spaCy Handles Entity Extraction:

- **Pre-trained Models**: spaCy comes equipped with models for various languages, adept at recognizing a plethora of entity types. These models, honed on extensive annotated datasets, exhibit a commendable generalization across diverse texts.

- **Tokenization**: As a precursor to entity detection, spaCy dissects the text into tokens, encompassing words and punctuation. This granular breakdown is instrumental in discerning potential entity boundaries.

- **Dependency Parsing**: In tandem with tokenization, spaCy deciphers the sentence's grammatical fabric, pinpointing inter-token relationships. This structural insight augments the context-sensitive detection of entities.

- **Entity Recognition Process**: Post token and relationship establishment, spaCy's NER module trawls the text, identifying sequences resonating with its trained entity patterns. Subsequently, it categorizes these sequences into preset buckets like `PERSON`, `ORG`, and `DATE`.

### Sample Code for Entity Extraction:

```python
# Import spaCy
import spacy

# Initialize the English NER model
nlp = spacy.load("en_core_web_sm")

# Sample text for processing
text = """Albert Einstein was a theoretical physicist. He developed the theory of relativity. Marie Curie was a chemist and physicist.
She discovered radium and polonium. Isaac Newton was an English mathematician, physicist, and astronomer. He is famous for his laws of motion and
the law of universal gravitation. Galileo Galilei was an Italian astronomer. He played a major role in the scientific revolution of the seventeenth century. He discovered Jupiter's four largest satellites.
"""
doc = nlp(text)

# Entity extraction and display
for entity in doc.ents:
    print(f"{entity.text} ({entity.label_})")
```
```
[('Albert Einstein', 'PERSON'), ('Marie Curie', 'PERSON'), ('Isaac Newton', 'PERSON'), ('English', 'LANGUAGE'), ('Galileo Galilei', 'PRODUCT'), ('Italian', 'NORP'), ('the seventeenth century', 'DATE'), ('Jupiter', 'LOC'), ('four', 'CARDINAL')]
 ```
## Entity Extraction using BERT

BERT (Bidirectional Encoder Representations from Transformers) has been a game-changer in the NLP landscape. Its bidirectional training and deep contextual embeddings make it a prime candidate for tasks like entity extraction.

### How BERT Facilitates Entity Extraction:

- **Deep Contextual Embeddings**: BERT's architecture allows it to understand words in context, making it adept at distinguishing between different usages of the same word, a crucial aspect for entity recognition.

- **Transfer Learning**: BERT is pre-trained on a massive corpus, enabling it to capture general linguistic patterns. For entity extraction, this pre-trained model can be fine-tuned on labeled entity data, allowing it to specialize in recognizing specific entity types. The example we use here is of GeoBERT which is fine-tuned from SciBERT on the Geoscientific Corpus dataset. The model was trained on the Labeled Geoscientific Corpus dataset (~1 million sentences) (copyright :https://huggingface.co/botryan96/GeoBERT)

- **End-to-End Training**: Unlike traditional methods that might involve multiple stages, with BERT, you can design an end-to-end entity recognition system, simplifying the pipeline and potentially boosting performance.

### Sample Code for Entity Extraction using GeoBERT:

```python
#Read the PDF Content
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    pdf_reader = PdfReader(pdf_path)
    pdf_text = ""

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_text += page.extract_text()

    return pdf_text

# Replace 'Your_PDF_Name.pdf' with the name of the uploaded PDF (to reproduce the result access the article at https://escholarship.org/uc/item/4m56569q)
pdf_text = extract_text_from_pdf('eScholarship UC item 4m56569q.pdf')
print(pdf_text[:1000])  # Print the first 1000 characters to check




from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import torch

# Load pre-trained BERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("botryan96/GeoBERT")
model = AutoModelForTokenClassification.from_pretrained("botryan96/GeoBERT", from_tf=True)
ner_machine = pipeline('ner', model=model, tokenizer=tokenizer, aggregation_strategy="simple")


# Sample text
pdf_text = "Elon Musk is the CEO of SpaceX."

# Tokenize input and get predictions
def extract_entities(text):
    # Split the text into chunks of 1000 characters
    text_chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    entities = []
    for chunk in text_chunks:
        entities += ner_machine(chunk)
    return [(entity['word'], entity['entity_group']) for entity in entities]

# Decode and display entities
entities = extract_entities(pdf_text)
print(entities[:50])  # Print the first 50 entities to check
```
```
[('velocity', 'GeoMeth'), ('glacier', 'GeoPetro'), ('##56', 'GeoLoc'), ('remote sensing', 'GeoMeth'), ('pune', 'GeoLoc'), ('remote sensing', 'GeoMeth'), ('velocity', 'GeoMeth'), ('glacier', 'GeoPetro'), ('##dar', 'GeoLoc'), ('velocity', 'GeoMeth'), ('glacier', 'GeoLoc'), ('remote sensing', 'GeoMeth'), ('remote sensing', 'GeoMeth'), ('vol', 'GeoMeth'), ('velocity', 'GeoMeth'), ('glacier', 'GeoPetro'), ('##dar', 'GeoLoc'), ('indian', 'GeoPetro'), ('india', 'GeoLoc'), ('geology', 'GeoMeth'), ('indian', 'GeoPetro'), ('india', 'GeoLoc'), ('earth', 'GeoPetro'), ('ir', 'GeoPetro'), ('##vin', 'GeoPetro'), ('usa', 'GeoLoc'), ('hydrologic', 'GeoMeth'), ('modeling', 'GeoMeth'), ('usa', 'GeoLoc'), ('usa', 'GeoLoc'), ('glacier', 'GeoPetro'), ('water cycle', 'GeoMeth'), ('himalayan', 'GeoPetro'), ('glaciers', 'GeoPetro'), ('india', 'GeoLoc'), ('glacier', 'GeoPetro'), ('aperture', 'GeoMeth'), ('radar', 'GeoMeth'), ('offset', 'GeoMeth'), ('thermal', 'GeoMeth'), ('glacier', 'GeoLoc'), ('glacier', 'GeoLoc'), ('velocity', 'GeoMeth'), ('glacier', 'GeoLoc'), ('glacier', 'GeoLoc'), ('velocity', 'GeoMeth'), ('glacier', 'GeoLoc'), ('uncertainty', 'GeoMeth'), ('glacier', 'GeoLoc'), ('climate change', 'GeoMeth')]
```

```python
# Test the ner_machine pipeline on a small text chunk
test_chunk = pdf_text[:1000]
test_entities = ner_machine(test_chunk)
print(test_entities)

[{'entity_group': 'GeoMeth', 'score': 0.98896956, 'word': 'velocity', 'start': 102, 'end': 110}, {'entity_group': 'GeoPetro', 'score': 0.70181453, 'word': 'glacier', 'start': 123, 'end': 130}, {'entity_group': 'GeoLoc', 'score': 0.49017197, 'word': '##56', 'start': 197, 'end': 199}, {'entity_group': 'GeoMeth', 'score': 0.96155363, 'word': 'remote sensing', 'start': 237, 'end': 251}, {'entity_group': 'GeoLoc', 'score': 0.90600884, 'word': 'pune', 'start': 293, 'end': 297}, {'entity_group': 'GeoMeth', 'score': 0.9892937, 'word': 'remote sensing', 'start': 732, 'end': 746}, {'entity_group': 'GeoMeth', 'score': 0.9860805, 'word': 'velocity', 'start': 895, 'end': 903}, {'entity_group': 'GeoPetro', 'score': 0.7499879, 'word': 'glacier', 'start': 916, 'end': 923}, {'entity_group': 'GeoLoc', 'score': 0.6558047, 'word': '##dar', 'start': 964, 'end': 967}]

```
