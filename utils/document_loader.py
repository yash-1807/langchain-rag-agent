from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import nltk

# Download necessary NLTK packages
print("Downloading NLTK data...")
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
print("NLTK data downloaded.")

# Define the data path
DATA_PATH = r"data\books"
print(f"Using data path: {DATA_PATH}")

# Define a dictionary to map file extensions to their respective loaders
loaders = {
    '.txt': TextLoader,
    '.csv': CSVLoader,
    '.md': UnstructuredMarkdownLoader
}

# Define a function to create a DirectoryLoader for a specific file type
def create_directory_loader(file_type, directory_path):
    print(f"Creating DirectoryLoader for {file_type} in {directory_path}")
    return DirectoryLoader(
        path=directory_path,
        glob=f"**/*{file_type}",
        loader_cls=loaders[file_type],
    )

# Create DirectoryLoader instances for each file type
try:
    txt_loader = create_directory_loader('.txt', DATA_PATH)
    csv_loader = create_directory_loader('.csv', DATA_PATH)
    md_loader = create_directory_loader('.md', DATA_PATH)
except Exception as e:
    print(f"Error creating loaders: {e}")

# Load the files
try:
    print("Loading .txt files...")
    txt_documents = txt_loader.load()
    print(f"Loaded {len(txt_documents)} .txt documents.")
except Exception as e:
    print(f"Error loading .txt files: {e}")

try:
    print("Loading .csv files...")
    csv_documents = csv_loader.load()
    print(f"Loaded {len(csv_documents)} .csv documents.")
except Exception as e:
    print(f"Error loading .csv files: {e}")

try:
    print("Loading .md files...")
    md_documents = md_loader.load()
    print(f"Loaded {len(md_documents)} .md documents.")
except Exception as e:
    print(f"Error loading .md files: {e}")

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
    return documents

def load_documents():
    documents = []
    try:
        print("Combining all loaded documents...")
        documents = txt_documents + csv_documents + md_documents
        print(f"Total documents loaded: {len(documents)}")

        print("Tagging documents with access levels...")
        documents = tag_documents(documents)
        print("Access levels tagged successfully.")
    except Exception as e:
        print(f"Error combining documents: {e}")
    return documents
