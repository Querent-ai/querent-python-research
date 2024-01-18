# Querent

The Asynchronous Data Dynamo and Graph Neural Network Catalyst

![image](https://github.com/Querent-ai/querent-ai/assets/61435908/39124a0c-3d9e-434f-9b54-9aa51dcefbd7)



## Unlock Insights, Asynchronous Scaling, and Forge a Knowledge-Driven Future

🚀 **Async at its Core**: Querent thrives in an asynchronous world. With asynchronous processing, we handle multiple data sources seamlessly, eliminating bottlenecks for utmost efficiency.

💡 **Knowledge Graphs Made Easy**: Constructing intricate knowledge graphs is a breeze. Querent's robust architecture simplifies building comprehensive knowledge graphs, enabling you to uncover hidden data relationships.

🌐 **Scalability Redefined**: Scaling your data operations is effortless with Querent. We scale horizontally, empowering you to process multiple data streams without breaking a sweat.

🔬 **GNN Integration**: Querent seamlessly integrates with Graph Neural Networks (GNNs), enabling advanced data analysis, recommendation systems, and predictive modeling.

🔍 **Data-Driven Insights**: Dive deep into data-driven insights with Querent's tools. Extract actionable information and make data-informed decisions with ease.

🧠 **Leverage Language Models**: Utilize state-of-the-art language models (LLMs) for text data. Querent empowers natural language processing, tackling complex text-based tasks.

📈 **Efficient Memory Usage**: Querent is mindful of memory constraints. Our framework uses memory-efficient techniques, ensuring you can handle large datasets economically.

## Table of Contents

- [Querent](#querent)
  - [Unlock Insights, Asynchronous Scaling, and Forge a Knowledge-Driven Future](#unlock-insights-asynchronous-scaling-and-forge-a-knowledge-driven-future)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
  - [Querent: an asynchronous engine for LLMs](#querent-an-asynchronous-engine-for-llms)
  - [Ease of Use](#ease-of-use)
  - [Contributing](#contributing)
  - [License](#license)

## Introduction

Querent is designed to simplify and optimize data collection and processing workflows. Whether you need to scrape web data, ingest files, preprocess text, or create complex knowledge graphs, Querent offers a flexible framework for building and scaling these processes.

## Features

- **Collectors:** Gather data from various sources asynchronously, including web scraping and file collection.

- **Ingestors:** Process collected data efficiently with custom transformations and filtering.

- **Processors:** Apply asynchronous data processing, including text preprocessing, cleaning, and feature extraction.

- **Storage:** Store processed data in various storage systems, such as databases or cloud storage.

- **Workflow Management:** Efficiently manage and scale data workflows with task orchestration.

- **Scalability:** Querent is designed to scale horizontally, handling large volumes of data with ease.

## Getting Started

Let's get Querent up and running on your local machine.

### Prerequisites

- Python 3.9+
- Virtual environment (optional but recommended)

### Installation

1. Clone the Querent repository:

   ```bash
   git clone https://github.com/querent-ai/querent-ai.git
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

Querent provides a flexible framework that adapts to your specific data collection and processing needs. Here's how to get started:

1. **Configuration:** Set up collector, ingestor, and processor configurations as needed.

2. **Collecting Data:** Implement collector classes to gather data from chosen sources. Handle errors and edge cases gracefully.

3. **Processing Data:** Create ingestors and processors to clean, transform, and filter collected data. Apply custom logic to meet your requirements.

4. **Storage:** Choose your storage system (e.g., databases) and configure connections. Store processed data efficiently.

5. **Task Orchestration:** For large tasks, implement a task orchestrator to manage and distribute the workload.

6. **Scaling:** To handle scalability, consider running multiple instances of collectors and ingestors in parallel.

7. **Monitoring:** Implement monitoring and logging to track task progress, detect errors, and ensure smooth operation.

8. **Documentation:** Maintain thorough project documentation to make it easy for others (and yourself) to understand and contribute.

## Configuration

Querent relies on configuration files to define how collectors, ingestors, and processors operate. These files are typically located in the `config` directory. Ensure that you configure the components according to your project's requirements.

## Querent: an asynchronous engine for LLMs

**Sequence Diagram:** *Asynchronous Data Processing in Querent*

```mermaid
sequenceDiagram
    participant User
    participant Collector
    participant Ingestor
    participant Processor
    participant LLM
    participant Querent
    participant Storage
    participant Callback

    User->>Collector: Initiate Data Collection
    Collector->>Ingestor: Collect Data
    Ingestor->>Processor: Ingest Data
    Processor->>LLM: Process Data (IngestedTokens)
    LLM->>Processor: Processed Data (EventState)
    Processor->>Storage: Store Processed Data (CollectedBytes)
    Ingestor->>Querent: Send Ingested Data (IngestedTokens)
    Querent->>Processor: Process Ingested Data (IngestedTokens)
    Processor->>LLM: Process Data (IngestedTokens)
    LLM->>Processor: Processed Data (EventState)
    Callback->>Storage: Store Processed Data (EventState)
    Querent->>Processor: Processed Data Available (EventState)
    Processor->>Callback: Return Processed Data (EventState)
    Callback->>User: Deliver Processed Data (CollectedBytes)

    Note right of User: Asynchronous Flow
    Note right of Collector: Data Collection
    Note right of Ingestor: Data Ingestion
    Note right of Processor: Data Processing
    Note right of LLM: Language Model Processing
    Note right of Querent: Query Execution
    Note right of Storage: Data Storage
    Note right of Callback: Callback Invocation

```

## Ease of Use

With Querent, creating scalable workflows with any LLM is just a few lines of code.

```python
import pytest
import uuid
from pathlib import Path
import asyncio

from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_code import IngestedCode
from querent.common.types.ingested_images import IngestedImages
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from querent.core.base_engine import BaseEngine
from querent.querent.querent import Querent
from querent.querent.resource_manager import ResourceManager
from querent.collectors.collector_resolver import CollectorResolver
from querent.common.uri import Uri
from querent.config.collector.collector_config import FSCollectorConfig
from querent.ingestors.ingestor_manager import IngestorFactoryManager

# Create input and output queues
input_queue = QuerentQueue()
resource_manager = ResourceManager()


# Define a simple mock LLM engine for testing
class MockLLMEngine(BaseEngine):
    def __init__(self, input_queue: QuerentQueue):
        super().__init__(input_queue)

    async def process_tokens(self, data: IngestedTokens):
        if data is None or data.is_error():
            # the LLM developer can raise an error here or do something else
            # the developers of Querent can customize the behavior of Querent
            # to handle the error in a way that is appropriate for the use case
            self.set_termination_event()
            return
        # Set the state of the LLM
        # At any given point during the execution of the LLM, the LLM developer
        # can set the state of the LLM using the set_state method
        # The state of the LLM is stored in the state attribute of the LLM
        # The state of the LLM is published to subscribers of the LLM
        current_state = EventState(EventType.Graph, 1.0, "anything", "dummy.txt")
        await self.set_state(new_state=current_state)

    async def process_code(self, data: IngestedCode):
        pass

    async def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    async def process_images(self, data: IngestedImages):
        return super().process_images(data)

    def validate(self):
        return True


@pytest.mark.asyncio
async def test_example_workflow_with_querent():
    # Initialize some collectors to collect the data
    directory_path = "./tests/data/pdf4"
    collectors = [
        CollectorResolver().resolve(
            Uri("file://" + str(Path(directory_path).resolve())),
            FSCollectorConfig(root_path=directory_path, id=str(uuid.uuid4())),
        )
    ]

    # Connect to the collector
    for collector in collectors:
        await collector.connect()

    # Set up the result queue
    result_queue = asyncio.Queue()

    # Create the IngestorFactoryManager
    ingestor_factory_manager = IngestorFactoryManager(
        collectors=collectors, result_queue=result_queue
    )

    # Start the ingest_all_async in a separate task
    ingest_task = asyncio.create_task(ingestor_factory_manager.ingest_all_async())

    ### A Typical Use Case ###
    # Create an engine to harness the LLM
    llm_mocker = MockLLMEngine(input_queue)

    # Define a callback function to subscribe to state changes
    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            print(f"New state: {event_state}")
            print(f"New state type: {event_type}")
            assert event_state.event_type == EventType.Graph

    # Subscribe to state change events
    # This pattern is ideal as we can expose multiple events for each use case of the LLM
    llm_mocker.subscribe(EventType.Graph, StateChangeCallback())

    ## one can also subscribe to other events, e.g. EventType.CHAT_COMPLETION ...

    # Create a Querent instance with a single MockLLM
    # here we see the simplicity of the Querent
    # massive complexity is hidden in the Querent,
    # while being highly configurable, extensible, and scalable
    # async architecture helps to scale to multiple querenters
    # How async architecture works:
    #   1. Querent starts a worker task for each querenter
    #   2. Querenter starts a worker task for each worker
    #   3. Each worker task runs in a loop, waiting for input data
    #   4. When input data is received, the worker task processes the data
    #   5. The worker task notifies subscribers of state changes
    #   6. The worker task repeats steps 3-5 until termination
    querent = Querent(
        [llm_mocker],
        resource_manager=resource_manager,
    )
    # Start the querent
    querent_task = asyncio.create_task(querent.start())
    await asyncio.gather(ingest_task, querent_task)


if __name__ == "__main__":
    asyncio.run(test_example_workflow_with_querent())


```

## Contributing

Contributions to Querent are welcome! Please follow our [contribution guidelines](CONTRIBUTING.md) to get started.

## License

This project is licensed under the BSL-1.1 License - see the [LICENSE](LICENCE) file for details.
