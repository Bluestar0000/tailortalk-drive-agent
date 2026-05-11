import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)

@tool
def search_drive(q: str) -> str:
    """Search Google Drive using a Drive API query string."""
    try:
        folder_id = os.getenv("DRIVE_FOLDER_ID", "")
        service = get_drive_service()
        full_query = f"('{folder_id}' in parents) and ({q}) and trashed = false"
        results = service.files().list(
            q=full_query,
            pageSize=20,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc",
        ).execute()
        files = results.get("files", [])
        if not files:
            return "No files found matching your query."
        output = f"Found {len(files)} file(s):\n\n"
        for f in files:
            name = f.get("name", "Unnamed")
            modified = f.get("modifiedTime", "")[:10]
            link = f.get("webViewLink", "#")
            output += f"- {name} | Modified: {modified} | {link}\n"
        return output
    except Exception as e:
        return f"Drive API error: {str(e)}"

@tool
def list_all_files(dummy: str = "") -> str:
    """List all files in the Google Drive folder."""
    return search_drive("mimeType != 'application/vnd.google-apps.folder'")