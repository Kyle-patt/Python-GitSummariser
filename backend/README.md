# GitSummarizer — Backend API

FastAPI backend service for **GitSummarizer**, an AI-powered documentation and release notes tool for GitHub repositories and commits.

---

## 🚀 Features

- **Repository Summarizer (`POST /api/v1/summaries/repository`)**: Fetches repo metadata, README, and recent commits from the GitHub REST API and generates structured overviews (overview, key features, prerequisites, beginner-friendly explanation).
- **Commit Summarizer / Release Notes (`POST /api/v1/summaries/commit`)**: Analyzes git commit diffs, commit messages, and changed files to produce structured release notes and bug fix categorizations.
- **Search History & Persistence (`GET /api/v1/history`)**: Stores all generated summaries in SQLite via SQLAlchemy ORM with pagination, type filtering, and search.
- **Robust URL Parser (`backend/app/utils/url_parser.py`)**: Validates repository and commit URLs, strips `.git` and trailing slashes, enforces strict `github.com` host matching (SSRF prevention).
- **OpenAI Structured Outputs**: Uses official OpenAI Python SDK with Pydantic response models for guaranteed schema conformance and security-hardened system prompts against prompt injection.
- **Health & Monitoring (`GET /health`)**: Database connectivity and service health checks.
- **CORS Configured**: Ready for local Vite/React frontend integration.

---

## 📁 Directory Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py                    # Database dependency injection
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py          # GET /health
│   │       │   ├── history.py         # GET /history, GET /history/{id}, DELETE /history/{id}
│   │       │   └── summaries.py       # POST /summaries/repository, POST /summaries/commit
│   │       └── router.py              # Aggregated v1 router
│   ├── core/
│   │   └── exceptions.py              # Domain exceptions & error definitions
│   ├── models/
│   │   └── summary.py                 # SQLAlchemy SummaryRecord ORM model
│   ├── schemas/
│   │   ├── common.py                  # HealthResponse, ErrorResponse
│   │   ├── request.py                 # RepoSummaryRequest, CommitSummaryRequest
│   │   └── summary.py                 # Structured AI schemas & API response models
│   ├── services/
│   │   ├── ai_service.py              # OpenAI SDK with structured outputs
│   │   ├── github_service.py          # GitHub REST API client (httpx)
│   │   └── orchestrator.py            # Workflow pipeline (URL -> GitHub -> AI -> DB)
│   ├── utils/
│   │   └── url_parser.py              # GitHub URL and commit parser & validator
│   ├── config.py                      # Pydantic Settings & environment variables
│   ├── database.py                    # SQLite engine & session management
│   └── main.py                        # FastAPI application entry point & CORS
├── tests/
│   ├── conftest.py                    # In-memory SQLite fixtures & TestClient
│   ├── test_ai_service.py             # AI service unit tests
│   ├── test_api.py                    # End-to-end API integration tests
│   ├── test_database.py               # SQLAlchemy ORM tests
│   ├── test_github_service.py         # GitHub API client tests
│   └── test_url_parser.py             # URL parser & validator tests
├── .env.example                       # Template for required environment variables
├── .gitignore                         # Python/database ignore rules
├── requirements.txt                   # Production & testing dependencies
├── run.py                             # Development server runner
└── pytest.ini                         # Pytest configuration
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- (Optional) Git

### 2. Virtual Environment Setup
```bash
# Navigate to the project root
cd c:/Projects/LABMENTIX/GitSummarizer

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` file to `.env`:
```bash
cp backend/.env.example .env
```
Edit `.env` and set your API keys:
```env
# Required for AI generation:
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional but recommended to prevent GitHub API rate limits (60 req/hr unauthenticated):
GITHUB_TOKEN=your_github_personal_access_token_here

# Database URL (defaults to SQLite file in workspace):
DATABASE_URL=sqlite:///./git_summarizer.db

# Frontend origin allowed for CORS:
FRONTEND_ORIGIN=http://localhost:5173
```

---

## 🏃 Running the Application

### Development Server
```bash
python backend/run.py
```
Or with Uvicorn directly:
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will start at:
- **API Base**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc Documentation**: `http://127.0.0.1:8000/redoc`
- **Health Check**: `http://127.0.0.1:8000/health`

---

## 📡 API Endpoints

### 1. Repository Summary
- **Endpoint**: `POST /api/v1/summaries/repository`
- **Body**:
  ```json
  {
    "repo_url": "https://github.com/psf/requests"
  }
  ```
- **Response** (`201 Created`):
  ```json
  {
    "id": "c138f6d2-64f3-4217-915f-c00ea4f13dd4",
    "repo_url": "https://github.com/psf/requests",
    "repo_owner": "psf",
    "repo_name": "requests",
    "commit_sha": null,
    "summary_type": "repository",
    "title": "psf/requests Overview",
    "content": {
      "project_overview": "Requests is an elegant and simple HTTP library for Python, built for human beings.",
      "key_features": [
        "Keep-Alive & Connection Pooling",
        "International Domains and URLs",
        "Sessions with Cookie Persistence",
        "Browser-style SSL Verification"
      ],
      "prerequisites": [
        "Python 3.8+"
      ],
      "beginner_friendly_explanation": "Think of Requests like a postal service for your Python code—it handles packing your message, addressing it to the web server, and bringing back the response cleanly."
    },
    "repo_metadata": {
      "stars": 52000,
      "language": "Python"
    },
    "created_at": "2026-11-04T09:40:00Z"
  }
  ```

### 2. Commit Release Notes
- **Endpoint**: `POST /api/v1/summaries/commit`
- **Body**:
  ```json
  {
    "repo_url": "https://github.com/psf/requests",
    "commit_sha": "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"
  }
  ```
- **Response** (`201 Created`): Returns structured release notes (`concise_summary`, `important_features`, `bug_fixes`, `release_notes`).

### 3. History List & Search
- **Endpoint**: `GET /api/v1/history?limit=20&offset=0&summary_type=repository`
- **Response** (`200 OK`):
  ```json
  {
    "total": 1,
    "items": [ ... ]
  }
  ```

### 4. History Item by ID
- **Endpoint**: `GET /api/v1/history/{summary_id}`
- **Delete Item**: `DELETE /api/v1/history/{summary_id}` (`204 No Content`)

### 5. Health Check
- **Endpoint**: `GET /health`
- **Response**:
  ```json
  {
    "status": "ok",
    "app_name": "GitSummarizer API",
    "version": "1.0.0",
    "database": "connected",
    "timestamp": "2026-11-04T09:40:00.000000"
  }
  ```

---

## 🧪 Testing

Run all unit and integration tests using `pytest`:
```bash
python -m pytest backend/tests -v
```
All external GitHub and OpenAI calls are mocked in tests, ensuring tests execute quickly without incurring API charges or requiring active internet access.

