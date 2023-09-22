# Tokenizer Summary

Tokenization is the process of converting input text into a list of tokens. In the context of transformers, tokenization includes splitting the input text into words, subwords, or symbols (like punctuation) that are used to train the model.
(https://huggingface.co/docs/transformers/tokenizer_summary)

Three types of tokenizer we will explain:

- Byte-Pair Encoding (BPE)

- WordPiece

- SentencePiece


# Byte-Pair Encoding (BPE)

Byte-Pair Encoding (BPE) is a subword tokenization method that is used to represent open vocabularies effectively. It was originally introduced for byte-level compression but has since been adapted for tokenization in natural language processing, especially in neural machine translation.

## How BPE Works

1. **Initialization**: Start by representing each word as a sequence of characters, plus a special end-of-word symbol (e.g., `</w>`).

2. **Iterative Process**: Repeatedly merge the most frequent pair of consecutive symbols or characters.

3. **Stop**: The process can be stopped either after a certain number of merges or when a desired vocabulary size is achieved.

## Example

Consider the vocabulary: `['low', 'lower', 'newest', 'widest']` and we want to apply BPE.

1. **Initialization**:

```
low</w> -> l o w </w>
lower</w> -> l o w e r </w>
newest</w> -> n e w e s t </w>
widest</w> -> w i d e s t </w>

```

2. **Iterative Process**:
- First merge: `e` and `s` are the most frequent pair, so merge them to form `es`.
- Second merge: `es` and `t` are now the most frequent pair, so merge them to form `est`.
- Continue this process until the desired number of merges is achieved.

3. **Result**:
After several iterations, we might end up with subwords like `l`, `o`, `w`, `e`, `r`, `n`, `es`, `est`, `i`, `d`, `t`, and `</w>`.

## Language Models Using BPE

BPE has been used in various state-of-the-art language models and neural machine translation models. Some notable models include:

- **OpenAI's GPT-2**: This model uses a variant of BPE for its tokenization.
- **BERT**: While BERT primarily uses WordPiece, it's conceptually similar to BPE.
- **Transformer-based Neural Machine Translation models**: Such as those in the "Attention is All You Need" paper.

BPE allows these models to handle rare words and out-of-vocabulary words by breaking them down into known subwords, enabling more flexible and robust tokenization.

## Conclusion

Byte-Pair Encoding is a powerful tokenization technique that bridges the gap between character-level and word-level tokenization. It's especially useful for languages with large vocabularies or for tasks where out-of-vocabulary words are common.

For more in-depth information, refer to the original [BPE paper](https://arxiv.org/abs/1508.07909).

# WordPiece Tokenization

WordPiece is a subword tokenization method that is widely used in various state-of-the-art natural language processing models. It's designed to efficiently represent large vocabularies.

## How WordPiece Works

1. **Initialization**: Begin with the entire training data's character vocabulary.

2. **Subword Creation**: Iteratively create subwords by choosing the most frequent character or character combination. This combination can be a new character sequence or a combination of existing subwords.

3. **Stop**: The process is usually stopped when a desired vocabulary size is reached.

## Example

Consider the vocabulary: `['unwanted', 'unwarranted', 'under']` and we want to apply WordPiece.

1. **Initialization**:
```
unwanted -> u n w a n t e d
unwarranted -> u n w a r r a n t e d
under -> u n d e r
```

2. **Iterative Process**:
- First merge: `un` might be the most frequent subword, so it's kept as a subword.
- Second merge: `wa` or `ed` might be the next most frequent, and so on.
- Continue this process until the desired vocabulary size is achieved.

3. **Result**:
After several iterations, we might end up with subwords like `un`, `wa`, `rr`, `ed`, `d`, `e`, and so on.

## Language Models Using WordPiece

WordPiece has been adopted by several prominent models in the NLP community:

- **BERT**: BERT uses WordPiece for its tokenization, which is one of the reasons for its success in handling a wide range of NLP tasks.
- **DistilBERT**: A distilled version of BERT, also uses WordPiece.
- **MobileBERT**: Optimized for mobile devices, this model also employs WordPiece tokenization.

The advantage of WordPiece is its ability to break down out-of-vocabulary words into subwords present in its vocabulary, allowing for better generalization and handling of rare words.

## Conclusion

WordPiece tokenization strikes a balance between character-level and word-level representations, making it a popular choice for models that need to handle diverse vocabularies without significantly increasing computational requirements.

For more details, you can refer to the [BERT paper](https://arxiv.org/abs/1810.04805) where WordPiece tokenization played a crucial role.


# SentencePiece Tokenization

SentencePiece is a data-driven, unsupervised text tokenizer and detokenizer mainly for Neural Network-based text generation systems where the vocabulary size is predetermined prior to the neural model training. SentencePiece implements subword units (e.g., byte-pair-encoding (BPE) and unigram language model with the extension of direct training from raw sentences).

## How SentencePiece Works

1. **Training**: SentencePiece trains tokenization model from raw sentences and does not require any preliminary tokenization.

2. **Vocabulary Management**: Instead of words, SentencePiece handles the texts as raw input and the spaces are treated as a special symbol, allowing consistent tokenization for any input.

3. **Subword Regularization**: Introduces randomness in the tokenization process to improve robustness and trainability.

## Example

Consider training SentencePiece on a dataset with sentences like `['I love machine learning', 'Machines are the future']`.

1. **Initialization**:
   The text is treated as raw, so spaces are also considered symbols.

2. **Iterative Process**:
   Using algorithms like BPE or unigram, frequent subwords or characters are merged or kept as potential tokens.

3. **Result**:
   After training, a sentence like `I love machines` might be tokenized as `['I', '▁love', '▁machines']`.

## Language Models Using SentencePiece

SentencePiece has been adopted by several models and platforms:

- **ALBERT**: A lite version of BERT, ALBERT uses SentencePiece for its tokenization.
- **T2T (Tensor2Tensor)**: The Tensor2Tensor library from Google uses SentencePiece for some of its tokenization.
- **OpenNMT**: This open-source neural machine translation framework supports SentencePiece.
- **LLAMA2**: this open source model uses SentencePiece.

The advantage of SentencePiece is its flexibility in handling multiple languages and scripts without the need for pre-tokenization, making it suitable for multilingual models and systems.

## Conclusion

SentencePiece provides a versatile and efficient tokenization method, especially for languages with complex scripts or for multilingual models. Its ability to train directly on raw text and manage vocabularies in a predetermined manner makes it a popular choice for modern NLP tasks.

For more details and implementation, you can refer to the [SentencePiece GitHub repository](https://github.com/google/sentencepiece).



