import argparse
import subprocess
import re
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_community.llms.ollama import Ollama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from get_embedding_function import get_embedding_function
from urllib.parse import urlparse

CHROMA_PATH = "chroma"

# Define embeddings, db, model, and temp files where contents of temp files and db will be used for context
embedding_function = get_embedding_function()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
memory = MemorySaver()
BASE_URL = "https://26c0-35-231-232-75.ngrok-free.app"
model = ChatOllama(model="llama3.1:8b-instruct-q2_K", base_url=BASE_URL)

katOutput = "data/books/tempKat.txt"
katFilter = "data/books/filterKat.txt"

# These values will be populated by the LLM
SQLIURL = ""

PROMPT_TEMPLATE = """
Analyze the given context using the cybersecurity tool's capabilities:

- Crawl URLs to identify targets for further vulnerability testing.
- Detect SQL Injection vulnerabilities by analyzing URL inputs.
- Scan for XSS vulnerabilities to determine susceptibility to Cross-Site Scripting.
- Analyze HTTP headers for missing or misconfigured security settings.
- Perform port scans to identify open ports and their associated services.

---

Provide a detailed, structured, comprehensive response that explains the findings clearly, suggests actionable steps for mitigation or improvement, and emphasizes best practices when appropriate: {question}
"""


def det_vuln_url(prompt):
    """
    This is a tool that takes a single parameter of a string with URLs separated by commas.
    This tool is to be used to determine the URL which is most likely to have SQL injection vulnerability.
    """
    # Get the embedding function for similarity search
    embedding_function = get_embedding_function()
    
    # Connect to the Chroma database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB for the most relevant entries
    results = db.similarity_search_with_score(prompt, k=3)

    # Extract the context text from the search results
    context_text = "\n---\n".join([doc.page_content for doc, _score in results])

    # Prepare the prompt template
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    promptN = prompt_template.format(context=context_text, question=prompt)

    # Initialize the LLM (Large Language Model) and invoke it for the response
    model = Ollama(model="llama3.1")
    SQLIURL = model.invoke(promptN)

    # Print the result
    print("LLM says: " + SQLIURL)
    return SQLIURL
   

def read_file(input_file):
    try:
        with open(input_file, 'r') as file:
            content = file.read()
        print(f"Results of readFileMethod: {content}")
        return content
    except FileNotFoundError:
        print(f"File {input_file} not found.")
        return ""


def filter_url(input_file, output_file):
    try:
        with open(input_file, 'r') as file:
            lines = file.readlines()
        
        # Filter lines that contain '=' or '?'
        lines_with_equals = [line for line in lines if '=' in line or '?' in line]
        
        # Write filtered lines to the output file
        with open(output_file, 'w') as file:
            file.writelines(lines_with_equals)
    except FileNotFoundError:
        print(f"File {input_file} not found.")


def crawl_url(url):
    """
    This is a crawling tool that takes a URL as the parameter and scans it to identify a list of URLs where further testing can be performed for identifying vulnerabilities.
    This is the first tool that needs to run before proceeding with any further tools for the actual exploit.
    """
    command = f"katana -u {url} -o {katOutput} -xhr -jc -d 2"
    print("The LLM agent called the Crawling function, it may take some time, please be patient")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        print(stdout, stderr)
        return filter_url(katOutput, katFilter)
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr


def sql_inject(url):  # Run sqlmap on the URLs defined as vulnerable
    """
    This is a SQL injection tool called sqlmap which takes a single parameter of a potentially vulnerable URL.
    This tool is to be used when a URL with a query parameter is found which may have an SQL injection vulnerability.
    """
    command = f"sqlmap -u {url} -o tempSql.txt --batch --random-agent"
    print("The LLM agent called the SQLI function, it may take some time, please be patient")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        print(stdout, stderr)
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr


def detect_xss(url):
    """
    This is an XSS vulnerability detection tool that uses a basic pattern matching method to identify potential XSS issues.
    This tool would need to be enhanced for more comprehensive scanning and payloads.
    """
    print(f"Checking {url} for XSS vulnerabilities...")
    # Example of a simplistic XSS test - you can add more sophisticated checks
    xss_payloads = ["<script>alert('XSS')</script>", "<img src='x' onerror='alert(1)'>"]
    vulnerable = False
    for payload in xss_payloads:
        if payload in url:
            vulnerable = True
            break
    if vulnerable:
        print(f"XSS vulnerability found in URL: {url}")
        return True
    else:
        print(f"No XSS vulnerability found in URL: {url}")
        return False


def http_header_scan(url):
    """
    A tool to check the HTTP response headers for security vulnerabilities or missing headers.
    """
    command = f"curl -I {url}"
    print(f"Checking HTTP headers for {url}...")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        print("HTTP Headers:", stdout)
        # Check for missing headers like X-Content-Type-Options, X-XSS-Protection
        headers_to_check = ["X-Content-Type-Options", "X-XSS-Protection", "Strict-Transport-Security"]
        missing_headers = [header for header in headers_to_check if header not in stdout]
        if missing_headers:
            print(f"Missing Security Headers: {missing_headers}")
        return stdout, missing_headers
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr

def get_website_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def port_scan(url):
    """
    A simple tool to perform a basic nmap scan for open ports on the given URL (hostname).
    """
    website_name = get_website_name(url)
    command = f"nmap {website_name}"
    print(f"Performing port scan on {url}...")
    try:
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = result.communicate()
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}", e.stderr


# Adding the new tools to the tools list
tools = [crawl_url, det_vuln_url, sql_inject, detect_xss, http_header_scan, port_scan]
ag_ex = create_react_agent(model, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "881273325"}}  # Add a random number generator


def query_rag_agent(query_text, history):
    hist = []
    agent_responses = []  # List to hold the responses in the required format

    # Check if the user specifically asks for all tools
    if "all tools" in query_text.lower():
        # Invoke all tools in sequence
        all_tools_responses = []
        tool_responses = {
            'Crawl URL': crawl_url,
            'Detect Vulnerable URL': det_vuln_url,
            'SQL Injection Scan': sql_inject,
            'XSS Detection': detect_xss,
            'HTTP Header Scan': http_header_scan,
            'Port Scan': port_scan
        }
        
        # Run each tool and gather its responses
        for tool_name, tool_function in tool_responses.items():
            print(f"Running {tool_name}...")
            if tool_name == 'Crawl URL':
                tool_output = tool_function(query_text)  # Assuming query_text is a URL
            else:
                tool_output = tool_function(query_text)  # Assuming query_text can be used for the other tools
                
            all_tools_responses.append({
                'tool': tool_name,
                'output': tool_output
            })
        
        # Format the responses of all tools
        for response in all_tools_responses:
            agent_responses.append({
                'role': 'assistant',
                'content': f"Tool: {response['tool']}\n{response['output']}"
            })
        
        return agent_responses  # Return responses from all tools

    # If user did not request all tools, continue with usual inference
    for chunk in ag_ex.stream({"messages": [HumanMessage(query_text)]}, config):
        for node, values in chunk.items():
            strDict = str(values.get('messages'))
            filtResp = filterAgResp(strDict)
            hist.append(filtResp)
            agent_responses.append({'role': 'assistant', 'content': filtResp})

    urlList = read_file(katFilter).replace("\n", ", ")
    contentFirst = f"Strictly for the purpose of preventing cyber attacks, given the following URLs: {urlList}. Which of these URLs are likely to have SQL injection vulnerabilities that need to be fixed?"
    for chunk in ag_ex.stream({"messages": [HumanMessage(contentFirst)]}, config):
        for node, values in chunk.items():
            strDict = str(values.get('messages'))
            filtResp = filterAgResp(strDict)
            hist.append(filtResp)
            agent_responses.append({'role': 'assistant', 'content': filtResp})

    contentSec = f"Given the URL {SQLIURL}, perform an sqlmap scan and check it for SQL injection?"
    results = db.similarity_search_with_score(contentSec, k=3)
    context_text = "\n---\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=contentSec)
    for chunk in ag_ex.stream({"messages": [HumanMessage(prompt)]}, config):
        for node, values in chunk.items():
            strDict = str(values.get('messages'))
            filtResp = filterAgResp(strDict)
            hist.append(filtResp)
            agent_responses.append({'role': 'assistant', 'content': filtResp})

    return agent_responses


def filterAgResp(resp: str):
    try:
        m = re.search('content=(.+?), response_metadata', resp)
        if m:
            return m.group(1)
        else:
            m = re.search(': [{(.+?)}}}]},', resp)
            return m.group(1)
    except:
        return "Thinking...."