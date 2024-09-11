from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
import nltk

nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

DATA_PATH = "data/books"

# Define a dictionary to map file extensions to their respective loaders
loaders = {
    '.txt': TextLoader,
    '.csv': CSVLoader,
    '.md' : UnstructuredMarkdownLoader
}

# Define a function to create a DirectoryLoader for a specific file type
def create_directory_loader(file_type, directory_path):
    return DirectoryLoader(
        path=directory_path,
        glob=f"**/*{file_type}",
        loader_cls=loaders[file_type],
    )

# Create DirectoryLoader instances for each file type add more to ingest new data type
txt_loader = create_directory_loader('.txt', DATA_PATH)
csv_loader = create_directory_loader('.csv', DATA_PATH)
md_loader = create_directory_loader('.md', DATA_PATH)

# Load the files
txt_documents = txt_loader.load()
csv_documents = csv_loader.load()
md_documents = md_loader.load()

def load_documents():
    documents = []
    documents = txt_documents+csv_documents+md_documents
    print(documents)
    return documents