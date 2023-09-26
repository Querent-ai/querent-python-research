# Querent-AI Project Structure

This repository contains the Querent-AI project, organized into several folders, each serving a specific purpose in the data processing and knowledge discovery pipeline. Below is an overview of each folder:

## collectors
- Folder for data collection components.
- Collect data from various sources asynchronously, including web scraping, file collection, and more.

## common
- Common utility functions and shared code.
- Contains common types, configurations, and utilities used across the project.

## config
- Configuration files for Querent-AI.
- Contains settings and configurations for collectors, ingestors, processors, and other components.

## controllers
- Controllers for managing data processing workflows.
- Responsible for orchestrating tasks and managing the flow of data through the pipeline.

## dal
- Data Access Layer components.
- Handles interactions with databases or storage systems where processed data is stored.

## gnn
- Components related to Graph Neural Networks (GNNs).
- Integrates with GNNs for advanced data analysis, recommendation systems, and predictive modeling.

## ingestors
- Data ingestion components.
- Process collected data efficiently, applying custom transformations and filtering.

## insights
- Components for extracting insights from data.
- Provides tools to extract actionable insights, helping make data-informed decisions.

## kg
- Knowledge Graph components.
- Used to construct intricate knowledge graphs, connecting data points and revealing hidden relationships.

## lib
- External libraries and dependencies.
- Houses external libraries used by the project.

## llm
- Language Model components.
- Leverage state-of-the-art language models (LLMs) to process and understand text data.

## napper
- Components related to the Querent framework.
- Handles asynchronous data processing and task management.

## processors
- Data processing components.
- Applies asynchronous data processing, including text preprocessing, cleaning, and feature extraction.

## search
- Search-related components.
- Handles search functionality or integration with external search engines.

## storage
- Storage-related components.
- Responsible for storing processed data in various storage systems, such as databases or cloud storage.

## tools
- Tools and utilities for development and testing.
- May include scripts, testing tools, or other development aids.

## utils
- Utility functions and helper modules.
- Contains miscellaneous utility functions used throughout the project.

Each folder contains specific modules and code related to its functionality. Explore these folders to dive deeper into the Querent-AI project.
