# Querent-AI Project Structure

Welcome to the Querent-AI project! This repository is organized into several folders, each serving a specific purpose in the data processing and knowledge discovery pipeline. Below, you'll find an in-depth overview of each folder, along with examples and descriptions of their contents.

## collectors

- **Description:** This folder contains data collection components.
- **Purpose:** Collect data asynchronously from various sources, including web scraping, file collection, and more.
- **Examples:**
  - Web scraper for extracting data from websites.
  - File collectors to gather data from local and cloud-based files.
  - Blob storage connectors for cloud-based storage.
  - Streaming data collectors for real-time data collection.

## common

- **Description:** Common utility functions and shared code.
- **Purpose:** House common types, configurations, and utilities used across the project.
- **Examples:**
  - Utility functions for data processing.
  - Shared configurations and type definitions.

## config

- **Description:** Configuration files for Querent-AI.
- **Purpose:** Store settings and configurations for collectors, ingestors, processors, and other components.
- **Examples:**
  - Collector configurations specifying sources and collection settings.
  - Processor settings for text preprocessing.

## controllers

- **Description:** Controllers for managing data processing workflows.
- **Purpose:** Orchestrate tasks and manage the flow of data through the pipeline.
- **Examples:**
  - Workflow controllers that define how data moves through the system.
  - Task schedulers for parallel processing.

## dal

- **Description:** Data Access Layer components.
- **Purpose:** Handle interactions with databases or storage systems where processed data is stored.
- **Examples:**
  - Database connectors and query builders.
  - Storage adapters for cloud-based storage.

## gnn

- **Description:** Components related to Graph Neural Networks (GNNs).
- **Purpose:** Integrate with GNNs for advanced data analysis, recommendation systems, and predictive modeling.
- **Examples:**
  - GNN-based recommendation engines.
  - Graph algorithms for knowledge graph construction.

## ingestors

- **Description:** Data ingestion components.
- **Purpose:** Efficiently process collected data by applying custom transformations and filtering.
- **Examples:**
  - JSON and XML parsers for structured data.
  - Text ingestors for natural language data.

## insights

- **Description:** Components for extracting insights from data.
- **Purpose:** Provide tools to extract actionable insights, enabling data-informed decision-making.
- **Examples:**
  - Sentiment analysis models for customer feedback.
  - Statistical analysis tools for data trends.

## kg

- **Description:** Knowledge Graph components.
- **Purpose:** Construct intricate knowledge graphs, connecting data points and revealing hidden relationships.
- **Examples:**
  - Knowledge graph construction algorithms.
  - Graph visualization tools.

## lib

- **Description:** External libraries and dependencies.
- **Purpose:** Store external libraries used by the project.
- **Examples:**
  - Machine learning frameworks like TensorFlow or PyTorch.
  - Third-party libraries for data visualization.

## core

- **Description:** Neural Networks and Model components.
- **Purpose:** Leverage state-of-the-art language models (LLMs), NN models to process and understand text, contextual and semantic information.
- **Examples:**
  - LLM-based chatbots.
  - Text summarization models.
  - Knowledge Graph builders
  - Question Answering models
  - Multimodel models and building knowledge from images and text
  - Text classification models etc.

## querent

- **Description:** Components related to the Querent framework.
- **Purpose:** Handle asynchronous data processing and task management.
- **Examples:**
  - Querent engines for data processing.
  - Task queues for job scheduling.
  - Handles for managing asynchronous tasks.

## processors

- **Description:** Data processing components.
- **Purpose:** Apply asynchronous data processing, including text preprocessing, cleaning, and feature extraction.
- **Examples:**
  - Text tokenization and cleaning functions.
  - Feature extraction models.

## search

- **Description:** Search-related components.
- **Purpose:** Handle search functionality or integration with external search engines.
- **Examples:**
  - **Semantic Knowledge Graph Search** - Search for entities and relationships in the knowledge graph and infer new relationships.
  - **Full-text Search** - Search for text in the knowledge graph and return relevant results.
  - **Widgets** - Downloadable widgets for search integration with external applications.
  - Search integration with Elasticsearch etc.

Each folder plays a crucial role in the Querent-AI project, contributing to its data processing and knowledge discovery capabilities. Explore these folders to delve deeper into the project's inner workings and functionalities.
