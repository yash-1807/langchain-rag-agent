import argparse
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langgraph.checkpoint.memory import MemorySaver
from langchain.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
import subprocess
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

#define emmbeddings, db, model and temp files where contents of temp files and db will be used for context
embedding_function = get_embedding_function()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
memory = MemorySaver()
model = ChatOllama(model="llama3.1")
katOutput = "tempKat.txt"
katFilter = "filterKat.txt"

PROMPT_TEMPLATE = """
Answer the question based on the following context:

{context}

---

Answer the question in a few lines based on the above context: {question}
"""
def readFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()
    return content

def filterUrl(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Filter lines that contain '='
    lines_with_equals = [line for line in lines if '=' in line]
    
    # Write filtered lines to the output file
    with open(output_file, 'w') as file:
        file.write("Following urls may have query parameters\n")
        file.writelines(lines_with_equals)

def scanUrl(url):
    """
    This is a scanning tool that takes a url as the parameter to identify or check potential urls where vulnerablilties may exist
    This is the first tool that needs to run before proceeding with any further tools for the actual exploit
    """
    command = ("katana -u "+url+" -o "+katOutput+" -xhr -jc -d 2")
    print("The LLM agent called the Scanning function, it may take some time, please be patient")
    try:
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        filterUrl(katOutput,katFilter)
        return readFile(katFilter).replace("\n",", ")
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr

def sqlinject(url): #run sqlmap on the urls defined as vulnerable
    """
    This is a sqlinjection tool which takes a single parameter of a potentially vulnerable url
    This tool is to be used when a url with a query parameter ("=" present in the url) is found which may have an sql injection vulnerability
    """
    command = ("sqlmap -u "+url+" -o tempSql.txt --batch --random-agent")
    print("The LLM agent called the SQLI function, it may take some time, please be patient")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        print(stdout,stderr)
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr

def query_rag(query_text):
    tools = [scanUrl, sqlinject, ]
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    # Use the agent
    config = {"configurable": {"thread_id": "8812733"}}
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(query_text)]}, config
    ):
        print(chunk)
        print("----")

    urlList = readFile(katFilter).replace("\n",", ")
    contentSec = "given the url(s) in the list "+urlList+" which of these urls have an sql injection vulnerability if any at all?"
    results = db.similarity_search_with_score(contentSec, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=contentSec)
    #print(prompt)
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(prompt)]}, config
    ):
        print(chunk)
        print("----")

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

if __name__ == "__main__":
    main()