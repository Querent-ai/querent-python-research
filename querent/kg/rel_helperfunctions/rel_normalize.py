import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

# Make sure to download the required NLTK data:
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('stopwords')


class TextNormalizer:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    def lowercase(self, text):
        return text.lower()

    def lemmatize(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
        return ' '.join(lemmatized_tokens)

    def remove_stop_words(self, text):
        tokens = word_tokenize(text)
        filtered_tokens = [token for token in tokens if token not in self.stop_words]
        return ' '.join(filtered_tokens)

    def normalize(self, text):
        text = self.lowercase(text)
        text = self.lemmatize(text)
        text = self.remove_stop_words(text)
        return text
    
    def normalize_triples(self, triples):
        normalized_triples = []
        for triple in triples:
            entity1, context_json, entity2 = triple
            context_dict = json.loads(context_json)  # Assuming context_json is a JSON string
            normalized_context = self.normalize(context_dict['context'])
            context_dict['context'] = normalized_context  # Replace the context with the normalized one
            normalized_context_json = json.dumps(context_dict)  # Convert back to JSON string if needed
            normalized_triples.append((entity1, normalized_context_json, entity2))
        return normalized_triples

triples = [
  ('tectonic', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.11, "pair_attnscore": 0.15, "entity1_embedding": [4.785828113555908, 4.2147417068481445, 4.608402729034424, 7.86382532119751, -3.119875907897949, 6.4056620597839355, 4.736032962799072, 0.40054139494895935, -1.7422124147415161, 9.150322914123535], "entity2_embedding": [4.749422073364258, 3.777057647705078, 6.303576946258545, 8.151358604431152, -2.55820369720459, 5.3259968757629395, 6.484385967254639, 0.4279687702655792, -0.9084129333496094, 7.9470624923706055], "sentence_embedding": [-0.4015790522098541, 3.746861696243286, 6.176400661468506, 5.342568397521973, -0.9461199641227722, -6.17316198348999, -4.8703389167785645, 13.388699531555176, 8.222224235534668, 14.191060066223145]}', 'upstream'), 
  ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [4.75761604309082, 3.4331743717193604, 4.266805171966553, 8.083751678466797, -3.261979103088379, 5.861548900604248, 5.962497234344482, 0.6605709195137024, -1.374169945716858, 10.495802879333496], "entity2_embedding": [4.707525253295898, 3.565460205078125, 6.727005958557129, 7.980961322784424, -2.6597471237182617, 5.267481327056885, 6.5619893074035645, 0.22673408687114716, -0.8828330039978027, 8.61778736114502], "sentence_embedding": [0.15698224306106567, 3.8285863399505615, 6.090454578399658, 4.998751163482666, -2.00986647605896, -6.002192497253418, -4.941530704498291, 13.459432601928711, 8.741031646728516, 11.845033645629883]}', 'upstream'),
  ('deposition', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [4.505099773406982, 4.15098762512207, 4.646312713623047, 7.436164379119873, -3.1875975131988525, 6.197781085968018, 4.853282451629639, 0.5896610617637634, -0.9382550120353699, 9.722227096557617], "entity2_embedding": [4.713261127471924, 3.442910671234131, 6.62761926651001, 8.26006031036377, -2.7525744438171387, 5.223714351654053, 6.508554935455322, 0.2672390639781952, -1.0225239992141724, 8.644356727600098], "sentence_embedding": [0.1906796097755432, 3.833495616912842, 6.085261344909668, 4.97797966003418, -2.1924057006835938, -5.993052005767822, -4.952077865600586, 13.469947814941406, 8.780710220336914, 11.937219619750977]}', 'upstream')
]

# Instantiate the text normalizer
normalizer = TextNormalizer()

normalized_triples = normalizer.normalize_triples(triples)

print(normalized_triples)