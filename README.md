# Real-Time Social Media Sentiment Analysis with Apache Kafka

This project demonstrates a real-time data streaming pipeline for social media comments, leveraging Apache Kafka, Python for data processing, SQLite for persistence, and Streamlit for interactive visualization. 
It's designed to showcase key data engineering principles, including distributed messaging, stream processing, data transformation (ETL), and dashboarding.

## Table of Contents

* [Project Overview](#project-overview)
* [Features](#features)
* [Architecture](#architecture)
* [Technologies Used](#technologies-used)
* [Setup and Installation](#setup-and-installation)
    * [Prerequisites](#prerequisites)
    * [Clone the Repository](#clone-the-repository)
    * [Set up Python Virtual Environment](#set-up-python-virtual-environment)
    * [Install Python Dependencies](#install-python-dependencies)
    * [Download NLTK Data](#download-nltk-data)
    * [Set up Kafka with Docker Compose](#set-up-kafka-with-docker-compose)
* [How to Run the Pipeline](#how-to-run-the-pipeline)
    * [Start Kafka Cluster](#start-kafka-cluster)
    * [Run the Producer](#run-the-producer)
    * [Run the Consumer (Sentiment Analyzer & Raw Data Ingester)](#run-the-consumer-sentiment-analyzer--raw-data-ingester)
    * [Run the Data Transformer (Aggregator)](#run-the-data-transformer-aggregator)
    * [Run the Streamlit Dashboard](#run-the-streamlit-dashboard)
* [Database Schema](#database-schema)
    * [comments_sentiments_raw](#comments_sentiments_raw)
    * [comments_sentiments_aggregated](#comments_sentiments_aggregated)
* [Troubleshooting](#troubleshooting)
* [Future Enhancements](#future-enhancements)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)


### 1. Project Overview
In today's data-driven world, understanding public sentiment from social media in real-time is crucial for businesses. 
This project simulates a social media comment stream, analyzes the sentiment of each comment as it arrives, persists both raw and aggregated data, and provides an interactive dashboard for live monitoring of sentiment trends.

### 2. Features
* **Real-time Comment Generation**: A Python producer simulates continuous social media comments.

* **Apache Kafka Integration**: Comments are streamed to and consumed from Kafka topics, demonstrating distributed messaging.

* **Sentiment Analysis**: Python consumer processes comments in real-time, applying sentiment analysis (Positive, Neutral, Negative).

* **Data Persistence**: Raw comments and their sentiment, along with aggregated hourly metrics, are stored in an SQLite database.

* **Automated Data Transformation**: A Python script continuously aggregates raw data into hourly summaries.

* **Interactive Real-time Dashboard**: A Streamlit application visualizes sentiment trends and metrics, updating automatically.

* **Modular SQL Queries**: SQL queries for database schema creation and data manipulation are kept in separate files for better organization.

### 3. Architecture
The system follows an event-driven architecture:

+----------------+       +-------------------+       +-------------------+
| Python Producer| ----> | Apache Kafka      | ----> | Python Consumer   |
| (Simulated     |       | (Broker & ZK)     |       | (Sentiment       |
| Comments)      |       |                   |       |  Analyzer)        |
+----------------+       +-------------------+       +-------------------+
                                   |                           |
                                   V                           V
                          +-------------------------------------+
                          | SQLite Database (`sentiment_data.db`)|
                          | - `comments_sentiments_raw`         |
                          | - `comments_sentiments_aggregated`  |
                          +-------------------------------------+
                                   ^                           |
                                   |                           |
                          +----------------+                   |
                          | Python Data    | <-----------------+
                          | Transformer    | (Reads raw, writes aggregated)
                          | (Aggregator)   |
                          +----------------+
                                   |
                                   V
                          +--------------------+
                          | Streamlit Dashboard|
                          | (Reads aggregated  |
                          |  data for viz)     |
                          +--------------------+

### 4. Technologies Used
* **Apache Kafka**: Distributed streaming platform for building real-time data pipelines.

* **Python 3.x**: Primary language for producers, consumers, data transformers, and the dashboard.

* **`confluent-kafka-python`**: Python client for Kafka.

* **`TextBlob / nltk`**: For basic sentiment analysis (can be swapped for tweet-sentiment-pt for Portuguese).

* **`sqlite3`**: Python's built-in module for SQLite database interaction.

* **`pandas`**: Data manipulation and analysis.

* **`matplotlib / seaborn`**: Data visualization for the dashboard.

* **`streamlit`**: Rapid application development for interactive web dashboards.

* **Docker / Docker Compose**: Containerization for easy setup and management of the Kafka cluster.

### 5. Setup and Installation
#### Prerequisites

* Python 3.8+

* Docker Desktop (for Windows/macOS) or Docker Engine & Docker Compose (for Linux) installed and running.

#### Clone the Repository
```bash
git clone https://github.com/RodrigoSantanaAguiar/sentiment_analysis.git
cd your-repo-name
```

#### Set up Python Virtual Environment
It's highly recommended to use a virtual environment to manage dependencies.

```bash
python3 -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

#### Install Python Dependencies
With your virtual environment activated, install the required libraries:

Bash
```bash
pip install confluent-kafka nltk textblob pandas matplotlib seaborn streamlit
# (If you decide to use tweet-sentiment-pt for Portuguese sentiment analysis, install it here too: pip install tweet-sentiment-pt)
```

#### Download NLTK Data
The textblob library (which uses NLTK) requires some data for sentiment analysis. Run the following Python commands once:

```python
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')
# (You can put these lines in a temporary Python script and run it, then delete the script.)
```

#### Set up Kafka with Docker Compose
Ensure your docker-compose.yml file in the project root is configured as follows (this sets up a single Kafka broker with ZooKeeper):

```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  broker:
    image: confluentinc/cp-kafka:7.4.0
    hostname: broker
    container_name: broker
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:9093,PLAINTEXT_HOST://localhost:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
```

### 6. How to Run the Pipeline
You'll need multiple terminal windows/tabs, each with your Python virtual environment activated (source venv/bin/activate).

#### 1. Start Kafka Cluster
Navigate to the project root and start the Kafka and ZooKeeper containers:

```bash
docker-compose up -d
# Wait for 15-30 seconds for the Kafka broker to fully initialize before proceeding.
```

#### 2. Run the Producer
This script simulates social media comments and sends them to Kafka.

````bash
python producer.py
# You should see "Message delivered..." logs.
````

#### 3. Run the Consumer (Sentiment Analyzer & Raw Data Ingester)
This script consumes messages from Kafka, performs sentiment analysis, and saves raw data to comments_sentiments_raw table in SQLite.

```bash 
python consumer.py
# You should see logs indicating sentiment analysis and data saving. Let this run for at least 1-2 minutes to populate the raw table.
```

#### 4. Run the Data Transformer (Aggregator)
This script reads raw data from SQLite, aggregates it hourly by source and device, and saves it to comments_sentiments_aggregated table. It's designed to run continuously.

````bash
python data_transformer.py
# You should see "Data aggregated..." logs. Let this run for at least 30 seconds to populate the aggregated table.
````


#### 5. Run the Streamlit Dashboard
This script powers the interactive web dashboard, visualizing your aggregated sentiment data.

```bash
streamlit run dashboard_app.py
# This will open a new tab in your web browser (usually at http://localhost:8501). The dashboard will automatically update every few seconds to reflect new aggregated data.
```

#### Important: Cleaning Data for Reruns
To clear all data and start fresh (e.g., after modifying schema or source data):

* Stop all Python scripts (Ctrl+C in each terminal).

* Stop and remove Docker containers and their volumes: docker-compose down -v

* Delete the SQLite database file: rm sentiment_data.db (Linux/macOS) or del sentiment_data.db (Windows).

* Then, repeat the steps from "Start Kafka Cluster".


### 7. Troubleshooting
* `zsh: command not found: docker-compose`: Ensure Docker Desktop is installed and running, or Docker Compose is installed separately on Linux. Restart your terminal.


* `Disconnected while requesting ApiVersion / Producer/Consumer hangs`: Kafka might not be fully ready. Wait 15-30 seconds after docker-compose up -d before running Python scripts. Verify KAFKA_ADVERTISED_LISTENERS in docker-compose.yml is correctly set to PLAINTEXT://broker:9093,PLAINTEXT_HOST://localhost:9092.


* `KeyError in Pandas ('source', 'observation_time', etc.)`: This usually means the column wasn't present in the DataFrame when loaded from SQLite, likely due to an old database schema. Perform a complete cleanup (stop all, docker-compose down -v, rm sentiment_data.db) and restart the pipeline.


* "No data available" on Streamlit Dashboard: Ensure all parts of the pipeline (Kafka, Producer, Consumer, Aggregator) are running and the aggregator has had time to populate comments_sentiments_aggregated.


* Incorrect Sentiment Results (e.g., for Portuguese): The default TextBlob is optimized for English. For Portuguese, consider using tweet-sentiment-pt (requires changing the analyze_sentiment function in consumer.py and installing the package).


* Percentages are 0.0: This is due to integer division in SQL. Ensure you're multiplying by 1.0 (e.g., COUNT * 1.0 / TOTAL) in your aggregation query to force floating-point division.


* Aggregated data shows only one source/device: Ensure the source and device fields are being correctly generated by the producer, read by the consumer, and crucially, that your comments_sentiments_aggregated table has PRIMARY KEY (observation_time, device, source) defined. If not, perform a full cleanup and restart.


### 9. Future Enhancements
* **Portuguese Sentiment Analysis**: Integrate tweet-sentiment-pt or a Hugging Face transformers model for accurate Portuguese sentiment analysis.

* **Kafka Connect**: Explore using Kafka Connect to move data between Kafka and SQLite without writing custom consumer code.

* **Kafka Streams/Faust**: Implement more complex real-time aggregations or transformations directly on Kafka streams using Kafka Streams (Java/Scala) or Faust (Python).

* **PostgreSQL Integration**: Migrate from SQLite to PostgreSQL (running in Docker) to demonstrate experience with a more robust relational database, including features like native table partitioning.

* **More Advanced Dashboarding**: Add more interactive filters, different types of charts, or integrate machine learning insights into the Streamlit dashboard.

* **Unit/Integration Tests**: Add comprehensive tests for each component of the pipeline.

### 10. Contributing
Feel free to fork this repository, open issues, or submit pull requests.

### 11. License
This project is open-source and available under the MIT License.

### 12. Contact
[Rodrigo Santana Aguiar](https://www.linkedin.com/in/rodrigo-s-aguiar/)
