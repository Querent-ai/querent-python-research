import os
import nltk
import spacy

def test_spacy_and_nltk():
    model_path = os.getenv('MODEL_PATH', '/model/')
    nltk_data_path = os.path.join(model_path, 'nltk_data')
    spacy_model_path = os.path.join(model_path, 'en_core_web_lg-3.7.1/en_core_web_lg/en_core_web_lg-3.7.1')

    print(f"Expected NLTK data path: {nltk_data_path}")
    print(f"Expected spaCy model path: {spacy_model_path}")

    # Test NLTK
    nltk.data.path.append(nltk_data_path)
    try:
        # Attempt to load an NLTK resource to see if the path is correctly set
        nltk.data.find('tokenizers/punkt')
        print("NLTK data path is correctly set. NLTK data loaded from:", nltk.data.path)
    except LookupError:
        print("NLTK data path is not correctly set or the data is missing.")

    # Test spaCy
    try:
        # Attempt to load the spaCy model to see if the path is correctly set
        nlp = spacy.load(spacy_model_path)
        print("spaCy model loaded successfully. Model loaded from:", spacy_model_path)
    except IOError:
        print("spaCy model path is not correctly set or the model is missing.")

if __name__ == "__main__":
    test_spacy_and_nltk()
