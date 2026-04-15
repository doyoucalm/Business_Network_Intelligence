import os
from typing import Annotated, TypedDict, Union
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from .skills.lead_qualification import qualify_lead
from .skills.knowledge_base import product_search

# Environment Variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
APP_URL = os.getenv("APP_URL", "https://bnimahardika.qd.je")

# 1. State Definition
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. LLM Configuration (using OpenRouter via OpenAI-compatible SDK)
llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_URL,
    default_headers={
        "HTTP-Referer": APP_URL,
        "X-Title": "Mahardika Hub"
    },
    temperature=0.7
)

# 3. Modular Tools Integration
tools = [qualify_lead, product_search]
llm_with_tools = llm.bind_tools(tools)

# 4. Node Definitions
def assistant(state: State):
    """The central reasoning engine."""
    system_prompt = SystemMessage(content="""
    Anda adalah asisten AI modular untuk BNI Chapter Mahardika Hub.
    Tugas Anda adalah memproses kueri melalui WhatsApp secara natural.
    
    Gunakan alat 'qualify_lead' untuk mengevaluasi prospek baru.
    Gunakan alat 'product_search' untuk memberikan fakta akurat dari katalog.
    
    Jika Anda mendeteksi niat pembelian tinggi, beri tahu pengguna untuk menunggu konfirmasi admin.
    Gunakan Bahasa Indonesia yang ramah dan profesional.
    """)
    return {"messages": [llm_with_tools.invoke([system_prompt] + state["messages"])]}

# 5. Graph Construction
builder = StateGraph(State)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")

# Compile the graph
react_graph = builder.compile()

async def chat_with_ai(messages: list, context: str = "general") -> str:
    """Wrapper to interact with the LangGraph orchestration."""
    if not OPENROUTER_API_KEY:
        return "AI assistant belum dikonfigurasi. Silakan hubungi administrator."

    # Convert incoming dict messages to LangChain message objects
    langchain_messages = []
    for m in messages:
        if m["role"] == "user":
            langchain_messages.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            # In a real app, we'd handle tool calls too
            pass 

    # Run the graph
    inputs = {"messages": langchain_messages}
    result = await react_graph.ainvoke(inputs)
    
    # Return the last message from the assistant
    return result["messages"][-1].content
