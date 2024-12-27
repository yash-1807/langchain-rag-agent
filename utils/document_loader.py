from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
import os
import nltk

# Download necessary NLTK packages
print("Downloading NLTK data...")
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
print("NLTK data downloaded.")

# Define the data path
DATA_PATH = r"E:\access_control\langchain-rag-agent\data\books"
print(f"Using data path: {DATA_PATH}")

# Define a dictionary to map file extensions to their respective loaders
LOADERS = {
    '.txt': TextLoader,
    '.csv': CSVLoader,
    '.md': UnstructuredMarkdownLoader,
    '.xlsx':UnstructuredExcelLoader
}

def create_directory_loader(file_type, directory_path):
    """
    Create a DirectoryLoader for a specific file type.
    """
    try:
        print(f"Creating DirectoryLoader for {file_type} in {directory_path}")
        return DirectoryLoader(
            path=directory_path,
            glob=f"**/*{file_type}",
            loader_cls=LOADERS[file_type],
        )
    except Exception as e:
        print(f"Error creating loader for {file_type}: {e}")
        return None

def load_documents():
    """
    Dynamically load documents from DATA_PATH for all supported file types.
    """
    if not os.path.exists(DATA_PATH):
        print(f"Directory {DATA_PATH} does not exist. No documents to load.")
        return []

    documents = []
    for file_type, loader_cls in LOADERS.items():
        try:
            print(f"Loading {file_type} files...")
            loader = create_directory_loader(file_type, DATA_PATH)
            if loader:
                docs = loader.load()
                print(f"Loaded {len(docs)} {file_type} documents.")
                documents.extend(docs)
            else:
                print(f"Skipping {file_type} files due to loader creation error.")
        except Exception as e:
            print(f"Error loading {file_type} files: {e}")

    if not documents:
        print("No documents found to load.")
        return []

    print(f"Total documents loaded: {len(documents)}")
    documents = tag_documents(documents)  # Tag documents with access levels
    return documents

def tag_documents(documents):
    """
    Add metadata to each document indicating whether it's public or internal.
    
    Logic:
    - Files containing 'public' in the name are marked as public.
    - All other files are marked as internal.
    """
    for doc in documents:
        file_name = doc.metadata.get("source", "").lower()
        if "public" in file_name:
            doc.metadata["access_level"] = "public"
        else:
            doc.metadata["access_level"] = "internal"
    print("Documents tagged with access levels successfully.")
    return documents
