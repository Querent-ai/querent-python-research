
## Entity Extraction using BERT

BERT (Bidirectional Encoder Representations from Transformers) has been a game-changer in the NLP landscape. Its bidirectional training and deep contextual embeddings make it a prime candidate for tasks like entity extraction.

### How BERT Facilitates Entity Extraction:

- **Deep Contextual Embeddings**: BERT's architecture allows it to understand words in context, making it adept at distinguishing between different usages of the same word, a crucial aspect for entity recognition.

- **Transfer Learning**: BERT is pre-trained on a massive corpus, enabling it to capture general linguistic patterns. For entity extraction, this pre-trained model can be fine-tuned on labeled entity data, allowing it to specialize in recognizing specific entity types.

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
