"""
    Querent AI: The Asynchronous Data Dynamo and Graph Neural Network Catalyst
"""

from setuptools import setup, find_packages

# List of required packages
requirements = [
    "aiofiles==23.2.1",
    "aiohttp==3.9.4",
    "attrs==23.1.0",
    "azure-storage-blob==12.19.0",
    "beautifulsoup4==4.12.3",
    "boto3==1.26.146",
    "botocore==1.29.146",
    "bs4==0.0.1",
    "cachetools==5.3.3",
    "coverage==7.3.3",
    "dropbox==11.36.2",
    "fastembed==0.2.6",
    "ffmpeg-python==0.2.0",
    "gensim==4.3.2",
    "gguf==0.6.0",
    "google-api-python-client==2.105.0",
    "google-cloud-storage==2.14.0",
    "hdbscan==0.8.33",
    "jira==3.6.0",
    "jmespath==1.0.1",
    "joblib==1.2.0",
    "json5==0.9.24",
    "jsonmerge==1.9.0",
    "jsonschema==4.17.3",
    "kombu==5.2.4",
    "langchain==0.1.11",
    "langchain-community==0.0.25",
    "llama_cpp_python==0.2.15",
    "lxml==4.9.2",
    "moviepy==1.0.3",
    "newspaper3k==0.2.8",
    "newsapi-python==0.2.7",
    "nltk==3.8.1",
    "numpy==1.24.3",
    "openai==1.13.3",
    "openpyxl==3.1.2",
    "pandas==2.1.4",
    "pdfminer==20191125",
    "pdfplumber==0.10.0",
    "pillow==10.3.0",
    "prometheus-client==0.17.1",
    "psutil==5.9.8",
    "pybase64==1.3.1",
    "pydantic==2.6.4",
    "pydub==0.25.1",
    "pyjwt==2.4.0",
    "pylint==2.17.4",
    "pymupdf==1.24.0",
    "pyshacl==0.25.0",
    "pytesseract==0.3.10",
    "pytextract==2.0.1",
    "python-dotenv==1.0.0",
    "python-docx==1.1.0",
    "python-pptx==0.6.23",
    "rdflib==7.0.0",
    "redis==5.0.3",
    "regex==2023.5.5",
    "requests==2.31.0",
    "requests_html==0.10.0",
    "slack-sdk==3.26.1",
    "slack-sdk==3.26.1",
    "spacy==3.7.2",
    "speechrecognition==3.10.1",
    "tika==2.6.0",
    "tensorflow==2.14.0",
    "transformers==4.36.0",
    "unidecode==1.3.7",
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="querent",
    version="3.1.2",
    author="Querent AI",
    description="The Asynchronous Data Dynamo and Graph Neural Network Catalyst",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Querent-ai/querent-ai",
    project_urls={
        "Documentation": "https://github.com/Querent-ai/querent-ai/docs",
        "Issue Tracker": "https://github.com/Querent-ai/querent-ai/issues",
    },
    keywords=[
        "Graph Neural Network",
        "Scalability",
        "Data-Driven Insights",
        "GNN",
        "Async",
        "Knowledge Graphs",
        "KG",
        "Large Language Models",
        "asyncio",
        "Insights",
        "aysnchronous",
        "LLM",
        "transformers",
        "pytorch",
        "Llama-index",
        "AI",
        "Artificial Intelligence",
        "Neo4j",
        "Queues",
        "QuiAssisstant",
        "Collectors",
        "Data",
        "Data Science",
        "Data Engineering",
        "Data Analysis",
        "Data Analytics",
        "News",
        "NLP",
        "Natural Language Processing",
        "Text",
        "Text Analysis",
        "Deep Learning",
        "Graphs",
        "Graph Theory",
        "Graph Algorithms",
        "Graph Analytics",
        "Graph Databases",
        "Graph Processing",
        "Graph Mining",
        "Graph Neural Networks",
        "GNN",
        "GNNs",
        "Graph Neural Network",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        "Intended Audience :: Other Audience",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Widget Sets",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Typing :: Typed",
    ],
    python_requires=">=3.10, <3.11",
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=requirements,
    license="Business Source License 1.1",
)
