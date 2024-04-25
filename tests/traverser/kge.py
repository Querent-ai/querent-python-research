import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
import pandas as pd
from torch.nn.functional import cosine_similarity
import random
import numpy as np

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False


class TextEnhancedKGE(nn.Module):
    def __init__(self, entity_dim, relation_dim, entity_to_idx, relation_to_idx, bert_model_name='bert-base-uncased'):
        super(TextEnhancedKGE, self).__init__()
        self.entity_embeddings = nn.Embedding(len(entity_to_idx), entity_dim)
        self.relation_embeddings = nn.Embedding(len(relation_to_idx), relation_dim)
        self.sentence_projection = nn.Linear(768, relation_dim)
        self.bert_model = BertModel.from_pretrained(bert_model_name)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_model_name)
        self.score_layer = nn.Linear(entity_dim * 2 + relation_dim, 1)
        self.combined_projection = nn.Linear(entity_dim * 2 + relation_dim, 768)

        nn.init.xavier_uniform_(self.entity_embeddings.weight)
        nn.init.xavier_uniform_(self.relation_embeddings.weight)
        nn.init.xavier_uniform_(self.sentence_projection.weight)
        nn.init.xavier_uniform_(self.combined_projection.weight)

    def sentence_to_embedding(self, sentences):
        inputs = self.bert_tokenizer(sentences, return_tensors="pt", padding=True, truncation=True, max_length=500)
        outputs = self.bert_model(**inputs)
        return outputs.last_hidden_state[:, 0, :].squeeze()

    def forward(self, heads, relations, tails, sentences):
        print("Heads: ", heads)
        print("Relations: ", relations)
        print("Tensors: ", tails)
        print("Sets: ", sentences)
        head_embeddings = self.entity_embeddings(heads)
        print("head embeddings", head_embeddings)
        relation_embeddings = self.relation_embeddings(relations)
        tail_embeddings = self.entity_embeddings(tails)
        
        sentence_embeddings = self.sentence_to_embedding(sentences)
        projected_sentences = self.sentence_projection(sentence_embeddings)

        score = self.calculate_score(head_embeddings, relation_embeddings, tail_embeddings, projected_sentences)
        return score

    def calculate_score(self, head_embeddings, relation_embeddings, tail_embeddings, sentence_embeddings):
        combined_embeddings = torch.cat([head_embeddings, relation_embeddings + sentence_embeddings, tail_embeddings], dim=1)
        return self.score_layer(combined_embeddings)

    def query(self, query_text, heads, relations, tails, sentences):
        query_embedding = self.sentence_to_embedding([query_text]).unsqueeze(0)
        sentence_embeddings = self.sentence_to_embedding(sentences)
        projected_sentences = self.sentence_projection(sentence_embeddings)

        head_embeddings = self.entity_embeddings(heads)
        relation_embeddings = self.relation_embeddings(relations)
        tail_embeddings = self.entity_embeddings(tails)

        relation_plus_sentence = relation_embeddings + projected_sentences
        combined_embeddings = torch.cat([head_embeddings, relation_plus_sentence, tail_embeddings], dim=1)

        if combined_embeddings.shape[-1] != query_embedding.shape[-1]:
            combined_embeddings = self.combined_projection(combined_embeddings)

        similarities = cosine_similarity(query_embedding, combined_embeddings, dim=-1)
        return similarities

# Load your data
data = pd.read_csv('my_subgraph_data.csv')
print(data.head())
print(data.columns)
# Create mappings
entity_to_idx = {entity: idx for idx, entity in enumerate(pd.concat([data['Node Start'], data['Node End']]).unique())}
relation_to_idx = {relation: idx for idx, relation in enumerate(data['Relationship Type'].unique())}
print('Creating entity_to_idx and relation_to_idx', entity_to_idx)
print('2nd indx', relation_to_idx)

# Initialize the model
model = TextEnhancedKGE(
    entity_dim=100,
    relation_dim=100,
    entity_to_idx=entity_to_idx,
    relation_to_idx=relation_to_idx
)

# Prepare data for the model
heads = torch.LongTensor(data['Node Start'].map(entity_to_idx).values)
relations = torch.LongTensor(data['Relationship Type'].map(relation_to_idx).values)
tails = torch.LongTensor(data['Node End'].map(entity_to_idx).values)
sentences = data['Sentence'].tolist()

# Calculate scores
scores = model(heads, relations, tails, sentences)
print(scores)

# User query
query_text = "How does hydraulic fracturing enhance porosity?"
similarities = model.query(query_text, heads, relations, tails, sentences)
top_matches = similarities.topk(10)  # Get the top 10 matches as per revised requirement
print(top_matches)
