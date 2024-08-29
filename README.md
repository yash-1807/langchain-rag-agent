# Langchain RAG Setup & Collaboration Guide 
## Welcome cs team, please follow the following steps to setup the application.

## Install dependencies

1. Run this command to install dependenies in the `requirements.txt` file. 

```python
pip install -r requirements.txt
```
If any of the packages do not install, or throws errors, install them individually. Im sure you will figure it out.

2. Install markdown depenendies with: 

```python
pip install "unstructured[md]"
```

## Create database

Create the Chroma DB.

The command below will ingest the contents of the md file stored in the DATA_PATH = "data/books"

```python
python populate_database.py
```

## Query the database

Query the Chroma DB.

```python
python query_data.py "How does Alice meet the Mad Hatter?"
```

You'll also need to run ollama locally before running and of the python commands as this entire project runs locally, get the setup from the official page : https://ollama.com/. Once setup is completed, run the following commands in a terminal after closing any running instance of ollama.
```ollama
ollama pull llama3.1
ollama pull nomic-embed-text
ollama serve
```
>You are now good to run the python commands to create the database and query the LLM.

