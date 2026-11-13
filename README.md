# GitSummarizer

GitSummarizer is an AI-powered developer tool that simplifies how students, junior developers, and engineering leads digest public open-source codebases. Instead of deciphering dense README files and sprawling git logs, GitSummarizer parses public GitHub repositories or commit hashes and generates structured, beginner-friendly overviews and human-readable release notes.

---

## 🏛️ System Architecture

```text
  ┌─────────────────────────────────────────────────────────┐
  │                 React Frontend (Vite)                   │
  │              (Tailwind CSS UI Dashboard)                │
  └────────────────────────────┬────────────────────────────┘
                               │ HTTP JSON Requests
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │                   FastAPI Backend                       │
  │   - URL Parsing & Validation (SSRF defense)             │
  │   - GitHub REST API Service (httpx)                     │
  │   - AI Summarization Service (OpenAI SDK)               │
  │   - SQLAlchemy ORM & SQLite Persistence                 │
  └─────────────┬─────────────────────────────┬─────────────┘
                │                             │
    1. Fetch Repo / Diff Data     2. Structured Prompts
                │                             │
                ▼                             ▼
  ┌───────────────────────────┐ ┌───────────────────────────┐
  │      GitHub REST API      │ │     OpenAI LLM API        │
  │  (Metadata, README, Logs) │ │ (gpt-4o-mini / Structured)│
  └───────────────────────────┘ └───────────────────────────┘
                │                             │
                └──────────────┬──────────────┘
                               │
                        Persist History
                               ▼
  ┌─────────────────────────────────────────────────────────┐
  │             SQLite / PostgreSQL Database                │
  │       (summary_records: URLs, diffs, JSON data)         │
  └─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Backend)

For full backend documentation, see [backend/README.md](file:///c:/Projects/LABMENTIX/GitSummarizer/backend/README.md).

```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Configure environment
cp backend/.env.example .env

# 3. Run server
python backend/run.py
```

Swagger API documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

