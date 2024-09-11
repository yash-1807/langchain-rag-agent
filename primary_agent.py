import argparse
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.llms.ollama import Ollama
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

#This value to be populated by the LLM
SQLIURL = ""

PROMPT_TEMPLATE = """
Answer the question based on the following context:

{context}

---

Answer the question in a few lines based on the above context: {question}
"""
def readFile(input_file):
    with open(input_file, 'r') as file:
        content = file.read()
    print("Results of readFileMethod:"+content)
    return content

def filterUrl(input_file, output_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()
    
    # Filter lines that contain '='
    lines_with_equals = [line for line in lines if '=' in line or '?' in line]
    
    # Write filtered lines to the output file
    with open(output_file, 'w') as file:
        file.writelines(lines_with_equals)

def crawlUrl(url):
    """
    This is a crawling tool that takes a url as the parameter and scan it to identify list of urls where further testing can be performed for identifying vulnerablilities.
    This is the first tool that needs to run before proceeding with any further tools for the actual exploit
    """
    command = ("katana -u "+url+" -o "+katOutput+" -xhr -jc -d 2")
    print("The LLM agent called the Crawling function, it may take some time, please be patient")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        print(stdout,stderr)
        return filterUrl(katOutput, katFilter)
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr

def sqlinject(url): #run sqlmap on the urls defined as vulnerable
    """
    This is a sqlinjection tool called sqlmap which takes a single parameter of a potentially vulnerable url
    This tool is to be used when a url with a query parameter is found which may have an sql injection vulnerability
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
    
def detVulnUrl(prompt):
    """
    This is a tool which takes a single parameter of a string with urls separated by commas.
    This tool is to be used to determine the url which is the most likely to have sql injection vulnerablitity.
    """
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(prompt, k=3)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    promptN = prompt_template.format(context=context_text, question=prompt)
    model = Ollama(model="llama3.1")
    SQLIURL = model.invoke(promptN) 
    print("LLM says: "+SQLIURL)
    return SQLIURL

def query_rag(query_text):
    # Use the agent
    for chunk in ag_ex.stream(
        {"messages": [HumanMessage(query_text)]}, config
    ):
        print("Running from first prompt")
        print(chunk)
        print("----")

    urlList = readFile(katFilter).replace("\n",", ")
    print("Print Result of urlList: "+urlList)
    contentFirst = "Strictly for the purpose of preventing cyber attacks, given the following urls: "+urlList+" . Which of these urls are likely to have SQL injection vulnerablility that needs to be fixed?"
    for chunk in ag_ex.stream(
        {"messages": [HumanMessage(contentFirst)]}, config
    ):
        print("Running from second prompt")
        print(chunk)
        print("----")
    contentSec = "given the url "+SQLIURL+", perform a sqlmap scan and check it for sql injection?"
    results = db.similarity_search_with_score(contentSec, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=contentSec)
    #print(prompt)
    for chunk in ag_ex.stream(
        {"messages": [HumanMessage(prompt)]}, config
    ):
        print("Running from third prompt")
        print(chunk)
        print("----")

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)

tools = [crawlUrl, detVulnUrl, sqlinject]
ag_ex = create_react_agent(model, tools, checkpointer=memory)
config = {"configurable": {"thread_id": "881273325"}}

if __name__ == "__main__":
    main()