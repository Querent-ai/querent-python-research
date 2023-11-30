from langchain.document_loaders import PyPDFLoader

loader = PyPDFLoader("test_paper_1.pdf", extract_images=True)
pages = loader.load()
print(pages[6].page_content)