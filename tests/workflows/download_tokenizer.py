# import os
# from transformers import AutoTokenizer

# def download_tokenizer(model_name_or_path, save_directory):
#     # Load the tokenizer
#     tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    
#     # Ensure the save directory exists
#     os.makedirs(save_directory, exist_ok=True)
    
#     # Save the tokenizer
#     tokenizer.save_pretrained(save_directory)
#     print(f"Tokenizer saved to {save_directory}")

# if __name__ == "__main__":
#     model_name = "botryan96/GeoBERT"  # Replace with your model
#     save_dir = "/home/nishantg/querent-main/querent/tests/geobert_files"  # Replace with your desired save directory
#     download_tokenizer(model_name, save_dir)
