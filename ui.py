import gradio as gr
from query_data import query_llm
from query_data import query_rag
from primary_agent import query_rag_agent








def process_query_with_file(role, query_text, uploaded_files, history=None):
    """
    Process the query along with uploaded files and update the chat history.
    """
    if uploaded_files:
        print(f"Uploaded files received in process_query_with_file: {uploaded_files}")
    else:
        print("No files uploaded.")

        
    if history is None:
        history = []

    # Call the query_rag function and accumulate the response
    response = ""
    for step in query_rag(role, query_text, uploaded_files):  # Pass the uploaded files
        response = step[-1]['content']  # Get the latest assistant content

    # Update the history
    history.append({'role': 'user', 'content': f"[{role}] {query_text}"})
    history.append({'role': 'assistant', 'content': response})

    return history, history  # Return updated history for Chatbot and State


rag_interface = gr.Interface(
    fn=process_query_with_file,
    inputs=[
        gr.Radio(choices=["External", "Internal"], label="Select User Role"),
        gr.Textbox(placeholder="Ask a question related to additional training data.", scale=7),
        gr.File(label="Upload files (optional)", file_types=[".txt"], type="filepath", file_count="multiple"),  # File input with filepath
        gr.State()  # State to maintain chat history
    ],
    outputs=[
        gr.Chatbot(height=300, type="messages"),
        gr.State()  # Updated chat history
    ],
    title="SBI-CS-GPT 0.2 - Enhanced RAG with File Upload",
    description="Interact with the LLM incorporating RAG and upload files for contextual updates.",
)












def create_chat_interface3(fn, placeholder, title, description, examples=None):
    """
    Function to create a professional and clean chat interface.
    """
    return gr.Interface(
        fn=fn,
        inputs=[ 
            gr.Textbox(placeholder=placeholder, container=False, scale=7),
        ],
        outputs=gr.Chatbot(height=300, type="messages"),  # Updated to 'messages' format
        title=title,
        description=description,
        theme="soft",
        examples=examples,
        cache_examples=True,
        allow_flagging="never",  # Optional, can be removed if not needed
    )



def create_chat_interface(fn, placeholder, title, description, examples=None):
    """
    Function to create a professional and clean chat interface with file upload.
    """
    def process_query(role, query_text, file, history=None):
        """
        Process the query, handle file uploads, and update chat history.
        """
        if history is None:
            history = []

        # Process the file if provided
        file_content = None
        if file:
            with open(file.name, "r", encoding="utf-8") as f:
                file_content = f.read()  # Load file content for processing
        
        # Call the main function (role-based logic)
        response_text = ""
        for step in fn(role, query_text, file_content=file_content):  # Pass file content to the function
            response_text = step[-1]['content']  # Extract the latest assistant response

        # Update the chat history
        history.append({'role': 'user', 'content': f"[{role}] {query_text}"})
        history.append({'role': 'assistant', 'content': response_text})

        return history, history

    return gr.Interface(
        fn=process_query,
        inputs=[
            gr.Radio(choices=["External", "Internal"], label="Select User Role"),
            gr.Textbox(placeholder=placeholder, container=False, scale=7),
            gr.File(label="Drag and drop your files here (optional)", file_types=[".txt", ".pdf", ".csv"]),
            gr.State()  # State to manage the chat history
        ],
        outputs=[
            gr.Chatbot(height=300, type="messages"),
            gr.State()  # Display and update chat history
        ],
        title=title,
        description=description,
        theme="soft",
        examples=examples,
        cache_examples=True,
        allow_flagging="never",  # Optional, can be removed if not needed
    )

def create_chat_interfacee(fn, placeholder, title, description, examples=None):
    """
    Function to create a professional and clean chat interface without role selection.
    """
    def process_query(query_text, history=None):
        """
        Process the user query and update chat history.
        """
        if history is None:
            history = []

        # Call the LLM function and accumulate the response
        response = ""
        for step in fn(query_text):  # Consume the generator
            response = step[-1]['content']  # Get the latest assistant content

        # Update the history
        history.append({'role': 'user', 'content': query_text})
        history.append({'role': 'assistant', 'content': response})

        return history, history  # Return updated history for Chatbot and State

    return gr.Interface(
        fn=process_query,
        inputs=[
            gr.Textbox(placeholder=placeholder, container=False, scale=7),
            gr.State()  # State to manage the chat history
        ],
        outputs=[
            gr.Chatbot(height=300, type="messages"),
            gr.State()  # Display and update chat history
        ],
        title=title,
        description=description,
        theme="soft",
        examples=examples,
        cache_examples=True,
        allow_flagging="never",  # Optional, can be removed if not needed
    )

# Define the interfaces
basic_interface = create_chat_interfacee(
    fn=query_llm,
    placeholder="Ask me any question.",
    title="SBI-CS-GPT 0.1 - Basic LLM",
    description="Engage with the basic LLM model for general queries.",
)
'''rag_interface = create_chat_interface(
    fn=query_rag,
    placeholder="Ask a question related to additional training data.",
    title="SBI-CS-GPT 0.1 - RAG",
    description="Interact with the LLM that incorporates retrieval-augmented generation (RAG).",
)'''

agent_interface = create_chat_interface3(
    fn=query_rag_agent,
    placeholder="Ask the agent to perform a task (Currently supports SQL Injection testing).",
    title="SBI-CS-GPT 0.1 - Task Agent",
    description="Engage with an agent capable of performing specific tasks, such as testing sites for SQL injections.",
)

# Combine all interfaces into a tabbed layout for easy navigation
demo = gr.TabbedInterface([basic_interface, rag_interface, agent_interface],
                          ["LLM BASIC", "LLM RAG", "LLM Agent"])

# Launch the application
if __name__ == "__main__":
    demo.launch(share=True)