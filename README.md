# Langchain RAG Setup Guide 
## Welcome cs team, please follow the following steps to setup the application.

## Ollama da mama
You'll also need to run ollama locally before running any of the python commands as this entire project runs locally. Get the setup from the official page : https://ollama.com/. Once setup is completed, run the following commands in a terminal after closing any running instance of ollama.
```ollama
ollama pull llama3.1
ollama pull nomic-embed-text
ollama serve
```
>You are now good to continue with the setup.

## Install dependencies

1. Run this command to install dependenies in the `requirements.txt` file. 

```python
pip install -r requirements.txt
```
If any of the packages do not install correctly, or throws errors or there is a mismatch of dependencies, god be with you. Im sure you will figure it out.

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
python query_data.py "What is sqli?" or python primary_agent.py "Is the site xxx vulnerable?"
```
