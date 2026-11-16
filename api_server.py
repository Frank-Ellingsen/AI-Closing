"""
CLOSE-AI & Financial Close Control Room - Root API Server Entrypoint
Delegates to src.api.api_server.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.api.api_server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=True)
