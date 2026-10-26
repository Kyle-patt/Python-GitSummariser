\# GitSummarizer — Integration Contract



\## 1. Architecture



\- Frontend: React, Vite, Tailwind CSS

\- Backend: FastAPI

\- Database: SQLite for the initial development setup

\- Repository data: GitHub REST API

\- AI summaries: LLM provider to be selected and configured



\## 2. Backend responsibilities



\- Accept and validate GitHub repository URLs.

\- Retrieve repository metadata, README content, and commit information.

\- Generate structured repository summaries and commit digests.

\- Persist summary history when database integration is implemented.

\- Expose documented HTTP endpoints to the frontend.



\## 3. Frontend responsibilities



\- Provide a repository URL input.

\- Send requests to the backend API.

\- Display loading, success, and error states.

\- Render repository summaries and commit digests.

\- Keep API calls in a dedicated service module.



\## 4. Initial API contract



\### Health check



`GET /health`



Expected response:



```json

{

&#x20; "status": "ok"

}

```



\### Repository summary



`POST /api/v1/summaries`



Proposed request:



```json

{

&#x20; "repository\_url": "https://github.com/owner/repository"

}

```



The final response schema will be agreed upon before implementation.



\## 5. Integration rules



\- The backend teammate owns backend implementation.

\- The frontend teammate owns frontend implementation.

\- The team lead owns integration, shared contracts, and merge coordination.

\- Feature work must be submitted through pull requests.

\- Changes to shared API schemas must be communicated before merging.

\- Secrets and local environment files must never be committed.



