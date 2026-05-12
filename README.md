# TailorTalk Drive Agent

A conversational AI agent for Google Drive file discovery.

## Live Demo
https://tailortalk-drive-agent-3fqxzgz9n8yyirclrvnzrq.streamlit.app

## Tech Stack
- **Backend:** FastAPI + LangChain + Groq (llama-3.3-70b)
- **Frontend:** Streamlit
- **Search:** Google Drive API v3 with q parameter queries
- **Deploy:** Render (backend) + Streamlit Cloud (frontend)

## Features
- Natural language file search ("find all PDFs", "show images modified this month")
- Translates requests into Drive API query strings automatically
- Session analytics with query history and response times
- Multi-turn conversation memory
- Supports search by name, file type, content, and date

## Architecture
User → Streamlit → FastAPI → LangChain Agent → Drive API → Files

## Setup
See backend/.env.example for required environment variables.

## Note
Backend on Render free tier — first request after inactivity takes ~30s to wake up.
