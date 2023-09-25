# Vector Embeddings

Vector embeddings are mathematical representations of objects, such as words, documents, images, or videos, in a continuous vector space. These embeddings capture the semantic meaning or inherent properties of the objects, making them useful for various machine learning and deep learning tasks.

## What are Vector Embeddings?

At a high level, vector embeddings transform objects into fixed-size vectors in a way that similar objects are close to each other in the vector space, while dissimilar ones are farther apart. This transformation allows algorithms to understand and process complex objects in a more structured and meaningful manner.

## Types of Embeddings

### 1. Text Embeddings

- **Word Embeddings**: Represent individual words as vectors. Examples include Word2Vec, GloVe, and FastText.
- **Sentence/Document Embeddings**: Represent entire sentences or documents as vectors. Examples include Doc2Vec, BERT embeddings, and Universal Sentence Encoder.

### 2. Audio Embeddings

Audio embeddings capture the inherent properties of audio signals, such as pitch, tempo, and timbre. They are used in tasks like audio classification, speaker recognition, and music recommendation.

### 3. Image Embeddings

Image embeddings transform visual data into a vector space. These embeddings capture the content and context of images. Popular methods include embeddings from pre-trained models like VGG, ResNet, and Inception.

### 4. Video Embeddings

Video embeddings represent videos in a continuous vector space by capturing both spatial (image frames) and temporal (sequence of frames) information. They are crucial for tasks like video classification, recommendation, and anomaly detection.

### 5. Document Embeddings

Document embeddings represent entire documents, capturing the overall semantic meaning. They are used in tasks like document clustering, classification, and information retrieval.


## Point of Interest : Document Embeddings

Document embeddings are vector representations of entire documents or paragraphs. Unlike word embeddings, which represent individual words, document embeddings capture the overall semantic content and context of a document.

## Why Document Embeddings?

While word embeddings provide representations for individual words, in many tasks like document classification, similarity computation, or information retrieval, we need to understand the document as a whole. Document embeddings provide a holistic view of the entire document, making them suitable for such tasks.

## Methods for Generating Document Embeddings

### 1. Averaging Word Embeddings

One of the simplest methods is to average the word embeddings of all words in a document. This method, while straightforward, can be surprisingly effective for many tasks.

```python
import numpy as np
from gensim.models import Word2Vec

# Load a pre-trained Word2Vec model
model = Word2Vec.load("path_to_pretrained_model")

def document_embedding(doc):
    embeddings = [model[word] for word in doc if word in model.wv.vocab]
    return np.mean(embeddings, axis=0)
```

### 2. Doc2Vec

Doc2Vec, an extension of Word2Vec, is specifically designed to produce document embeddings. It considers the context of words along with a unique identifier for each document.

```python
from gensim.models import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

# Prepare data
documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(corpus)]

# Train a Doc2Vec model
model = Doc2Vec(documents, vector_size=100, window=2, min_count=1, workers=4)

# Get document vector
vector = model.infer_vector(["word1", "word2", "word3"])

```
### 3. Pre-trained Transformers

Benchmark :- https://huggingface.co/spaces/mteb/leaderboard

[Medium - Helper Code](https://medium.com/@ryanntk/choosing-the-right-embedding-model-a-guide-for-llm-applications-7a60180d28e3#id_token=eyJhbGciOiJSUzI1NiIsImtpZCI6IjZmNzI1NDEwMWY1NmU0MWNmMzVjOTkyNmRlODRhMmQ1NTJiNGM2ZjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIyMTYyOTYwMzU4MzQtazFrNnFlMDYwczJ0cDJhMmphbTRsamRjbXMwMHN0dGcuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTE2NTAxMzgwMDYxMDIzMzEyMTUiLCJlbWFpbCI6Im5ndXB0YTEwLnNsYkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwibmJmIjoxNjk1NDAwMTg0LCJuYW1lIjoibmlzaGFudCBndXB0YSIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NLaUE5UkI4V3ZlbmR0bEtGZDkxQUtudzhNazN5a0pueXVLSVotMTZkUzI9czk2LWMiLCJnaXZlbl9uYW1lIjoibmlzaGFudCIsImZhbWlseV9uYW1lIjoiZ3VwdGEiLCJsb2NhbGUiOiJlbiIsImlhdCI6MTY5NTQwMDQ4NCwiZXhwIjoxNjk1NDA0MDg0LCJqdGkiOiJkYTNjODAyODk5YjE5OWYyYTMzZWZiYzdiZTc5NWQ3OGU0OTE2MDNlIn0.UBAxb43TA3aYonYND2dSr18U359k_Us62yKYo-zsuPtMx2dy1YJ_xapuGDD6rR28tuJz0Iv0Du3rTtTSyHoFgyHZDaScbiLsHpRD234V6GwevO6slglc3j_WV_DtVE_bphfCk68SlyM7dPRk7ib8I-loiW4nT7-VBvqgRoRh1_W-Y3blhE_5-ziQX5Z6aASdpHduVXsxxvXqZ7qxFA-tAizbO1mcoHTiUE-N2oLecrNJD5N7ljNwSqML8J3WzFK3vTghnLW89NloDUGhS85ZJif8_kqaf9rokg2OAZpgb4BLeUZFFeiggXbNp1GDex8HdIzOFIdU0meabcLqWef8zQ)


Modern transformer models like BERT, RoBERTa, and DistilBERT can be used to obtain document embeddings by averaging the embeddings of all tokens or using the embedding of a special token (e.g., [CLS]).


1. BERT

```python
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    return outputs['last_hidden_state'][0].mean(dim=0).detach().numpy()

```

2. SentenceTransformers 

Is a Python framework for state-of-the-art sentence, text and image embeddings. (https://partee.io/2022/08/11/vector-embeddings/)

Install the Sentence Transformers library.

```python
import numpy as np

from numpy.linalg import norm
from sentence_transformers import SentenceTransformer

# Define the model we want to use (it'll download itself)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

sentences = [
  "That is a very happy person",
  "That is a happy dog",
  "Today is a sunny day"
]

# vector embeddings created from dataset
embeddings = model.encode(sentences)

# query vector embedding
query_embedding = model.encode("That is a happy person")

# define our distance metric
def cosine_similarity(a, b):
    return np.dot(a, b)/(norm(a)*norm(b))

# run semantic similarity search
print("Query: That is a happy person")
for e, s in zip(embeddings, sentences):
    print(s, " -> similarity score = ",
         cosine_similarity(e, query_embedding))

```
```python
Query: That is a happy person

That is a very happy person -> similarity score = 0.94291496
That is a happy dog -> similarity score = 0.69457746
Today is a sunny day -> similarity score = 0.25687605
```


## Conclusion

Vector embeddings play a pivotal role in modern machine learning and artificial intelligence systems. By converting complex objects into continuous vector representations, they enable algorithms to process and understand data in more nuanced and sophisticated ways.

For a deeper dive into each type of embedding and their applications, numerous research papers, tutorials, and courses are available online.

