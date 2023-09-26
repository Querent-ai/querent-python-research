
![image](https://github.com/Querent-ai/querent-ai/assets/61435908/9ea59cdc-9bad-4476-9367-c9901c560dd4)

# Querent

**Querent: Unleash the Power of Data and Graph Neural Networks**
*Unlock Insights, Scale Asynchronously, and Forge a Knowledge-Driven Future*

**Welcome to Querent!** We're not just another data framework; we're the future of knowledge discovery and insight generation. Querent is your agile and dynamic companion for collecting, processing, and harnessing data's transformative potential. Whether you're crafting knowledge graphs, training cutting-edge language models, or diving deep into data-driven insights, Querent has your back.

🚀 **Async Unleashed**: Querent thrives in an asynchronous universe. With the power of asynchronous processing, we seamlessly juggle multiple data sources, ensuring that no insight is left undiscovered. Say goodbye to bottlenecks and hello to efficiency.

💡 **Knowledge Graphs Galore**: Construct intricate knowledge graphs effortlessly. Querent's robust architecture paves the way for the creation of comprehensive knowledge graphs, empowering you to connect the dots and unveil hidden relationships within your data.

🌐 **Scalability Redefined**: Scaling your data operations has never been this smooth. Querent scales horizontally, allowing you to process a multitude of data streams without breaking a sweat. Expand your horizons, the sky's the limit.

🔬 **GNN and Beyond**: Querent doesn't stop at knowledge graphs. Our framework seamlessly integrates with Graph Neural Networks (GNNs), opening doors to advanced data analysis, recommendation systems, and predictive modeling.

🔍 **Insights at Your Fingertips**: Dive deep into data-driven insights with ease. Querent provides tools to extract actionable insights, helping you make data-informed decisions swiftly.

🧠 **Language Models at Work**: Leverage the power of state-of-the-art language models (LLMs) to process and understand text data. Querent fuels the future of natural language processing, empowering you to tackle complex text-based tasks.

📈 **Memory-Efficient Insights**: Querent understands that memory is precious. Our framework employs efficient memory management techniques, ensuring you can handle colossal datasets without breaking the bank.

## Table of Contents

- [Querent](#querent)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [License](#license)

## Introduction

Querent is a project aimed at simplifying and optimizing data collection and processing workflows. Whether you need to scrape web data, ingest files, preprocess text, or create complex knowledge graphs, Querent provides a flexible framework for building and scaling these processes.

## Features

- **Collectors:** Gather data from various sources asynchronously, including web scraping, file collection, and more.

- **Ingestors:** Process collected data efficiently, applying custom transformations and filtering.

- **Processors:** Apply asynchronous data processing, including text preprocessing, cleaning, and feature extraction.

- **Storage:** Store processed data in various storage systems, such as databases or cloud storage.

- **Workflow Management:** Efficiently manage and scale data workflows with task orchestration.

- **Scalability:** Querent is designed to scale horizontally, allowing you to handle large volumes of data.

## Getting Started

Follow these instructions to set up and run Querent on your local machine.

### Prerequisites

- Python 3.7+
- Virtual environment (optional but recommended)

### Installation

1. Clone the Querent repository:

   ```bash
   git clone https://github.com/your-username/querent.git
   cd querent
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the project dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Querent provides a flexible framework that you can adapt to your specific data collection and processing needs. To get started, you can follow these general steps:

1. **Configuration:** Set up collector, ingestor, and processor configurations in the appropriate directories.

2. **Collecting Data:** Implement collector classes to gather data from your chosen sources. Make sure to handle errors and edge cases gracefully.

3. **Processing Data:** Create ingestors and processors to clean, transform, and filter collected data. Apply custom logic to meet your requirements.

4. **Storage:** Choose a storage system (e.g., database) and configure the necessary connections. Store the processed data efficiently.

5. **Task Orchestration:** If handling a large number of tasks, implement a task orchestrator to manage and distribute the workload.

6. **Scaling:** To handle scalability, consider running multiple instances of collectors and ingestors in parallel.

7. **Monitoring:** Implement monitoring and logging to track the progress of tasks, detect errors, and ensure smooth operation.

8. **Documentation:** Keep your project well-documented to make it easy for others (and yourself) to understand and contribute.

## Configuration

Querent relies on configuration files to define how collectors, ingestors, and processors operate. These files are typically located in the `config` directory. Ensure that you configure the components according to your project's requirements.


## Ease of use
with quetent writing scalable workflows atop any llm is just few lines of code.

```python
import asyncio
import pytest
from querent.common.types.querent_queue import QuerentQueue
from querent.llm.base_llm import BaseLLM
from querent.napper.querent import Querent
from querent.napper.resource_manager import ResourceManager

# Create input and output queues
input_queue = QuerentQueue()
output_queue = QuerentQueue()
resource_manager = ResourceManager()

# Define a simple mock LLM class for testing
class MockLLM(BaseLLM):
    async def process_tokens(self, data):
        return f"Processed: {data}"

    def validate(self):
        return True

@pytest.mark.asyncio
async def test_querent_with_base_llm():
    # Put some input data into the input queue
    input_data = ["Data 1", "Data 2", "Data 3", None]
    for data in input_data:
        await input_queue.put(data)
    
    # Create a list of mock LLM instances
    num_llms = 1
    llms = [MockLLM(input_queue, output_queue) for _ in range(num_llms)]

    # Create a Querent instance
    querent = Querent(llms, num_workers=num_llms, resource_manager=resource_manager)

    # Start the Querent
    await querent.start()

    # Check the output queue for results and store them in a list
    results = []
    async for result in output_queue:
        results.append(result)

    # Assert that the results match the expected output
    expected_output = [
        "Processed: Data 1",
        "Processed: Data 2",
        "Processed: Data 3",
        "Processed: None"
    ]
    assert results == expected_output
```

## Contributing

Contributions to Querent are welcome! Please follow our [contribution guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the BSL-1.1 License - see the [LICENSE](LICENSE) file for details.
