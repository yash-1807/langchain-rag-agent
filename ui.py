import gradio as gr
from query_data import query_llm
from query_data import query_rag

def create_chat_interface(fn, placeholder, title, description, examples=None):
    """
    Function to create a professional and clean chat interface.
    """
    def process_query(role, query_text, history=None):
        """
        Process the query, filter context by user role, and update chat history.
        """
        if history is None:
            history = []

        # Initialize the response string
        response_text = ""

        # Consume the generator function (query_rag)
        for step in fn(role, query_text):
            response_text = step[-1]['content']  # Extract the latest assistant response

        # Append user query and assistant response to history
        history.append({'role': 'user', 'content': f"[{role}] {query_text}"})
        history.append({'role': 'assistant', 'content': response_text})

        return history, history  # Return updated history for Chatbot and State

    return gr.Interface(
        fn=process_query,
        inputs=[
            gr.Radio(choices=["External", "Internal"], label="Select User Role"),
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

rag_interface = create_chat_interface(
    fn=query_rag,
    placeholder="Ask a question related to additional training data.",
    title="SBI-CS-GPT 0.1 - RAG",
    description="Interact with the LLM that incorporates retrieval-augmented generation (RAG).",
)

# Combine all interfaces into a tabbed layout for easy navigation
demo = gr.TabbedInterface([basic_interface, rag_interface], 
                          ["LLM BASIC", "LLM RAG"])

# Launch the application
if __name__ == "__main__":
    demo.launch(share=True)
