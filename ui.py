import gradio as gr
from query_data import query_llm
from query_data import query_rag

def create_chat_interface(fn, placeholder, title, description, examples=None):
    """
    Function to create a professional and clean chat interface.
    
    Parameters:
    - fn (function): The function to handle user queries.
    - placeholder (str): Placeholder text for the input textbox.
    - title (str): Title of the interface.
    - description (str): Description of the interface.
    - examples (list, optional): List of example queries for users.
    
    Returns:
    - gr.Interface: The Gradio interface object.
    """
    return gr.Interface(
        fn=fn,
        inputs=[
            gr.Radio(choices=["External", "Internal"], label="Select User Role"),
            gr.Textbox(placeholder=placeholder, container=False, scale=7)
        ],
        outputs=gr.Chatbot(height=300, type="messages"),  # Updated to 'messages' format
        title=title,
        description=description,
        theme="soft",
        examples=examples,
        cache_examples=True,
        allow_flagging="never",  # Optional, can be removed if not needed
    )

# Creating interfaces with the provided functions and details
basic_interface = create_chat_interface(
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
