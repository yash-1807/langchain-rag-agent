import argparse
import os
import shutil
from langchain.schema.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from get_embedding_function import get_embedding_function
from langchain_chroma.vectorstores import Chroma
from utils.document_loader import load_documents

CHROMA_PATH = "chroma"
DATA_PATH = "data/books"

def populate_database():
    # Debugging: Start the population process
    print("Starting database population process...")

    # Check if the database should be cleared (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("Clearing Database")
        clear_database()

    # Load documents
    print(f"Looking for documents in {DATA_PATH}...")
    documents = load_documents()
    print("Documents loaded")
   
    print(f"Loaded {len(documents)} documents from {DATA_PATH}")
    for i, doc in enumerate(documents):
        access_level = doc.metadata.get("access_level", "internal")  # Default to internal if not specified
        print(f"Document {i + 1} tagged as {access_level}: {doc.metadata.get('source', 'No source')}")

    if not documents:
        print("No documents found to process. Exiting.")
        return

    # Split documents into chunks
    print("Splitting documents into chunks...")
    chunks = split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Add chunks to Chroma database
    print("Adding chunks to Chroma database...")
    add_to_chroma(chunks)
    print("Database population process complete.")

def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks.")
    return chunks

def add_to_chroma(chunks: list[Document]):
    # Debugging: Initialize Chroma
    print(f"Initializing Chroma database in {CHROMA_PATH}...")
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs
    print("Calculating chunk IDs...")
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Retrieve existing documents
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Add only new documents
    new_chunks = []
    for chunk in chunks_with_ids:
        print(f"Checking chunk ID: {chunk.metadata['id']}")
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding {len(new_chunks)} new documents to the database.")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("No new documents to add.")

def calculate_chunk_ids(chunks):
    # Debugging: Start calculating IDs
    print("Calculating chunk IDs for each document...")

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", 0)
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page metadata.
        chunk.metadata["id"] = chunk_id
        print(f"Generated chunk ID: {chunk_id}")

    return chunks

def clear_database():
    if os.path.exists(CHROMA_PATH):
        print(f"Clearing database at {CHROMA_PATH}...")
        shutil.rmtree(CHROMA_PATH)
    else:
        print("No existing database found to clear.")


if __name__ == "__main__":
    populate_database()
