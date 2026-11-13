"""
Convenience entry point for running the GitSummarizer FastAPI server.
Usage:
    python backend/run.py
"""
import uvicorn
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

if __name__ == "__main__":
    print("Starting GitSummarizer FastAPI backend...")
    print("Documentation will be available at http://127.0.0.1:8000/docs")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

