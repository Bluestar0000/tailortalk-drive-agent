import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage
from drive_tool import search_drive, list_all_files
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )

SYSTEM_PROMPT = """You are a Google Drive file assistant. Translate user requests into Drive API query strings and call tools.

Drive API query syntax:
- name contains 'word'
- name = 'exact name'
- mimeType = 'application/pdf'
- mimeType = 'application/vnd.google-apps.document'
- mimeType = 'application/vnd.google-apps.spreadsheet'
- mimeType = 'application/vnd.google-apps.presentation'
- mimeType = 'image/jpeg'
- fullText contains 'word'
- modifiedTime > '2024-01-01T00:00:00'
- combine with and / or

Rules:
- For browse or list all requests, call list_all_files
- For specific searches, call search_drive with a proper q string
- Never make up file names"""

def create_agent_executor():
    llm = get_llm()
    tools = [search_drive, list_all_files]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )

def format_history(chat_history: list) -> list:
    """Convert dict history to LangChain message objects."""
    messages = []
    for msg in chat_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages