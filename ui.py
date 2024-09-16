import gradio as gr
from query_data import query_llm
from query_data import query_rag
from primary_agent import query_rag_agent

basic = gr.ChatInterface(
    query_llm,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Ask me any question.", container=False, scale=7),
    title="SBI-CS-GPT 0.1",
    description="Ask the LLM any question",
    theme="soft",
    examples=["What will you call an 8 legged human?", "Are tomatoes vegetables?"],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear",
)
rag = gr.ChatInterface(
    query_rag,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Ask me a question which i have been taught.", container=False, scale=7),
    title="SBI-CS-GPT 0.1",
    description="Ask the LLM any question which it has been additionally trained on.",
    theme="soft",
    examples=["Tell me a basic sqlmap command to scan a site."],
    cache_examples=True,
    retry_btn=None,
    undo_btn="Delete Previous",
    clear_btn="Clear",
)
agent = gr.ChatInterface(
    query_rag_agent,
    chatbot=gr.Chatbot(height=300),
    textbox=gr.Textbox(placeholder="Ask the agent to perform a task. (Only does sql injection for now)", container=False, scale=7),
    title="SBI-CS-GPT 0.1",
    description="Ask the agent to test on a site",
    theme="soft",
    undo_btn="Delete Previous",
    clear_btn="Clear",
)

demo = gr.TabbedInterface([basic, rag, agent], ["LLM BASIC", "LLM RAG", "LLM AGENT"])

if __name__ == "__main__":
    demo.launch()