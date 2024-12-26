# RAG System and AI Agent

🌟 **Overview** 🌟

This project combines the power of Retrieval-Augmented Generation (RAG) and an AI Agent equipped with cybersecurity tools to deliver a robust system for context-aware question answering and automated cybersecurity operations. This project also includes a basic section which acts like a normal AI assistant.  Built using LangChain and Ollama, the system leverages advanced Large Language Models (LLMs) and a vector database to provide accurate, context-specific answers.
## ✨ Key Features ✨

-**Retrieval-Augmented Generation (RAG)**: Enables accurate, context-based responses by querying a ChromaDB vector database.

-**User Role Management**: Filters data access based on user roles (Internal or External) to ensure secure information retrieval.

-**Sensitive Data Redaction**
- - -
##  🛠 Tech Stack
-**LangChain**: Framework for LLM-based applications and agents.

-**Ollama**: Lightweight, customizable local LLM provider.

-**ChromaDB**: Vector database for semantic search.

-**Python**: Core programming language.
- - -
## Architecture

![WhatsApp Image 2024-12-12 at 15 36 38](https://github.com/user-attachments/assets/747f0e82-a11e-4477-820e-0faeba1431b8)


## How to use 
### Setting up the server
First of all to setup the server, create your account on ngrok and acquire the auth token. Now on google colab run the following commands - 

#### To create and run terminal 

```
!pip install colab-xterm

%load_ext colabxterm

%xterm

```
#### On terminal , run the following commands - 

##### Install ollama and run

```
curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.4.7 sh

ollama serve

ollama run llama3.1:8b-instruct-q2_K
```

#### Install ngrok on code block

```
!pip install pyngrok

```

#### Set your ngrok auth token

```
from pyngrok import ngrok


# Open a tunnel to port 11434
ngrok.set_auth_token("<your auth token>")


```

#### Open the terminal again

```
%xterm

```
#### Run the following command and us the link you get as base_url -

```
ngrok http 11434 --host-header="localhost:11434"

```
###  Now for on-prem setup
#### Pull embeddings
```
ollama pull nomic-embed-text
```
>You are now good to continue with the setup.
### 1. Clone the repository
Clone the repository on your system
```
git clone https://github.com/yash-1807/langchain-rag-agent.git
```
### 2. Install dependencies
 Run this command to install dependenies in the `requirements.txt` file. 
```python
pip install -r requirements.txt
```
### 3. Create Database
Create the Chroma DB.
The command below will ingest the contents of the md file stored in the DATA_PATH = "data/books"
```python
python populate_database.py
```
### 4. Query the database
Use ui.py or the command below -
```python
python query_data.py "What is sqli?" or python primary_agent.py "Is the site xxx vulnerable?"
```










