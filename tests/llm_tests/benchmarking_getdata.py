from datasets import load_dataset
import pandas as pd

# Load the WebNLG dataset
dataset = load_dataset("web_nlg", 'release_v1')

# The dataset is now loaded and can be used
print(dataset)

final_csv = []

#Total sentence, total subjects, objects, predicates
for split in dataset.keys():

    split_dataset = dataset[split]
    n = 0
    m = 0
    # Now, iterate over the data in this split
    for i, value in enumerate(split_dataset):
        m += 1
        sentences = ""
        triples = []
        subject = []
        objects = []
        predicate = []
    
        for sentence in value["lex"]["text"]:
            sentences = sentences + sentence

        for triple in value["modified_triple_sets"]["mtriple_set"][0]:
            #we have triples in each triple, means string of characters, split it by | and we will have each value, now this value we have to add to array
            if len(value["modified_triple_sets"]["mtriple_set"][0]) > 1:
                continue
            sop = triple.split("|")
            subject.append(sop[0])
            objects.append(sop[1])
            predicate.append(sop[2])

        final_csv.append([sentences, subject, objects, predicate])


data_for_csv = pd.DataFrame(final_csv, columns=["original text", "subjects", "objects", "predicates"])

csv_file_path = 'web_nlg_extract.csv'
data_for_csv.to_csv(csv_file_path, index=False)