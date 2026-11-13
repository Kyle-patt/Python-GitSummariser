"""
Integration tests for FastAPI endpoints: summaries, history, and health.
"""
import pytest
from unittest.mock import patch, AsyncMock
from backend.app.schemas.summary import RepoSummaryContent, CommitSummaryContent
from backend.app.core.exceptions import GitHubRepositoryNotFoundError, AIConfigurationError
from backend.app.models.summary import SummaryRecord


class TestAPIEndpoints:
    """Test suite for HTTP REST API contracts."""

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
        assert "version" in data

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["docs"] == "/docs"
        assert data["api_v1"] == "/api/v1"

    def test_repository_summary_success(self, client):
        mock_summary = RepoSummaryContent(
            project_overview="Expressive ORM library.",
            key_features=["Dataclasses support", "Async engine"],
            prerequisites=["Python 3.8+"],
            beginner_friendly_explanation="SQLAlchemy helps Python talk to databases effortlessly."
        )

        with patch("backend.app.services.orchestrator.github_service.get_repo_metadata", new_callable=AsyncMock) as mock_meta, \
             patch("backend.app.services.orchestrator.github_service.get_readme", new_callable=AsyncMock) as mock_readme, \
             patch("backend.app.services.orchestrator.github_service.get_recent_commits", new_callable=AsyncMock) as mock_commits, \
             patch("backend.app.services.orchestrator.ai_service.summarize_repository", new_callable=AsyncMock) as mock_ai:

            mock_meta.return_value = {
                "name": "sqlalchemy",
                "full_name": "sqlalchemy/sqlalchemy",
                "description": "The Database Toolkit for Python",
                "stars": 8000,
                "forks": 1200,
                "open_issues": 40,
                "language": "Python",
                "default_branch": "main",
                "topics": ["database", "orm"],
                "html_url": "https://github.com/sqlalchemy/sqlalchemy",
            }
            mock_readme.return_value = "# SQLAlchemy\nSQL toolkit."
            mock_commits.return_value = []
            mock_ai.return_value = mock_summary

            payload = {"repo_url": "https://github.com/sqlalchemy/sqlalchemy"}
            response = client.post("/api/v1/summaries/repository", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert data["repo_name"] == "sqlalchemy"
            assert data["summary_type"] == "repository"
            assert data["content"]["project_overview"] == "Expressive ORM library."
            assert "id" in data

    def test_repository_summary_invalid_url_rejected(self, client):
        payload = {"repo_url": "https://gitlab.com/not/github"}
        response = client.post("/api/v1/summaries/repository", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "Unsupported host" in data["detail"]

    def test_repository_summary_not_found(self, client):
        with patch("backend.app.services.orchestrator.github_service.get_repo_metadata", side_effect=GitHubRepositoryNotFoundError("Repo not found")):
            payload = {"repo_url": "https://github.com/nonexistent/repo"}
            response = client.post("/api/v1/summaries/repository", json=payload)
            assert response.status_code == 404
            data = response.json()
            assert data["error"] == "GitHubRepositoryNotFoundError"

    def test_commit_summary_success(self, client):
        mock_commit_summary = CommitSummaryContent(
            concise_summary="Added unit tests for router.",
            important_features=["Extended pytest coverage"],
            bug_fixes=[],
            release_notes="### Release Notes\n- Enhanced test suite coverage."
        )

        with patch("backend.app.services.orchestrator.github_service.get_repo_metadata", new_callable=AsyncMock) as mock_meta, \
             patch("backend.app.services.orchestrator.github_service.get_commit_detail", new_callable=AsyncMock) as mock_commit, \
             patch("backend.app.services.orchestrator.ai_service.summarize_commit", new_callable=AsyncMock) as mock_ai:

            mock_meta.return_value = {"full_name": "psf/requests", "description": "HTTP for Humans", "language": "Python"}
            mock_commit.return_value = {
                "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d",
                "short_sha": "7fd1a60",
                "message": "test: add router tests",
                "author": "Tester",
                "date": "2026-10-20",
                "files": [],
                "diff_text": ""
            }
            mock_ai.return_value = mock_commit_summary

            payload = {
                "repo_url": "https://github.com/psf/requests",
                "commit_sha": "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"
            }
            response = client.post("/api/v1/summaries/commit", json=payload)

            assert response.status_code == 201
            data = response.json()
            assert data["summary_type"] == "commit"
            assert data["commit_sha"] == "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"
            assert data["content"]["concise_summary"] == "Added unit tests for router."

    def test_commit_summary_missing_sha_validation_error(self, client):
        payload = {"repo_url": "https://github.com/psf/requests"}
        response = client.post("/api/v1/summaries/commit", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert "A valid commit SHA must be provided" in data["detail"]

    def test_history_list_and_pagination(self, client, db_session):
        # Insert 3 records
        for i in range(3):
            rec = SummaryRecord(
                repo_url=f"https://github.com/org/repo{i}",
                repo_owner="org",
                repo_name=f"repo{i}",
                summary_type="repository",
                title=f"Repo {i}",
                content={"overview": f"Summary {i}"}
            )
            db_session.add(rec)
        db_session.commit()

        # Query history
        response = client.get("/api/v1/history?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

    def test_get_history_by_id_and_delete(self, client, db_session):
        rec = SummaryRecord(
            repo_url="https://github.com/vuejs/core",
            repo_owner="vuejs",
            repo_name="core",
            summary_type="repository",
            title="vuejs/core Overview",
            content={"overview": "Vue.js framework"}
        )
        db_session.add(rec)
        db_session.commit()

        rec_id = rec.id

        # Get by ID
        get_resp = client.get(f"/api/v1/history/{rec_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == rec_id

        # Delete by ID
        del_resp = client.delete(f"/api/v1/history/{rec_id}")
        assert del_resp.status_code == 204

        # Confirm 404 after deletion
        get_again = client.get(f"/api/v1/history/{rec_id}")
        assert get_again.status_code == 404
        assert get_again.json()["error"] == "SummaryNotFoundError"

