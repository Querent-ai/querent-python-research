# import torch
# from transformers import BertForTokenClassification, BertForTokenClassification
# from transformers import BertTokenizer
# import safetensors.torch

# # Load TensorFlow model
# tf_model_path = "botryan96/GeoBERT"
# model = BertForTokenClassification.from_pretrained(tf_model_path, from_tf = True)

# # Save the PyTorch model
# pytorch_model_path = "/home/nishantg/querent-main/querent/tests/geobert_files/"
# model.save_pretrained(pytorch_model_path)

# # Load the PyTorch model
# pytorch_model = BertForTokenClassification.from_pretrained(pytorch_model_path)
# # tokenizer = BertTokenizer.from_pretrained(pytorch_model_path)

# # Save the PyTorch model in safetensors format
# output_path = "/home/nishantg/querent-main/querent/tests/geobert_files/model.safetensors"
# state_dict = pytorch_model.state_dict()
# safetensors.torch.save_file(state_dict, output_path)
