from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as file:
    requirements = file.read().splitlines()

setup(
    name="querent-ai",
    version="0.1",
    author="saraswatpuneet",
    description="The Asynchronous Data Dynamo and Graph Neural Network Catalyst",
    long_description="Querent is designed to simplify and optimize data collection and processing workflows. Whether you need to scrape web data, ingest files, preprocess text, or create complex knowledge graphs, Querent offers a flexible framework for building and scaling these processes.",
    url="https://github.com/Querent-ai/querent-ai",
    keywords="Graph Neural Network, Scalability, Data-Driven Insights",
    python_requires=">=3.9, <4",
    packages=find_packages(),
    install_requires=requirements,
    license="Business Source License 1.1",
    package_data={
        "sample": ["sample_data.csv"],
    },
    entry_points={
        "runners": [
            "sample=sample:main",
        ]
    },
)
