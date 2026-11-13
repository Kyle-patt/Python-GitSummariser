"""
Unit tests for the GitHub REST API service with mocked responses.
"""
import base64
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx

from backend.app.services.github_service import GitHubService
from backend.app.core.exceptions import (
    GitHubRepositoryNotFoundError,
    GitHubCommitNotFoundError,
    GitHubRateLimitError,
)


@pytest.fixture
def gh_service():
    return GitHubService(token="test_dummy_token", timeout=5.0)


class TestGitHubService:
    """Test suite for GitHubService methods and error mappings."""

    async def test_get_repo_metadata_success(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_error = False
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "fastapi",
            "full_name": "tiangolo/fastapi",
            "description": "FastAPI framework, high performance, easy to learn.",
            "stargazers_count": 75000,
            "forks_count": 6000,
            "open_issues_count": 200,
            "language": "Python",
            "default_branch": "master",
            "topics": ["fastapi", "python", "api"],
            "html_url": "https://github.com/tiangolo/fastapi",
            "created_at": "2018-12-05T00:00:00Z",
            "updated_at": "2026-10-01T00:00:00Z",
        }

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            metadata = await gh_service.get_repo_metadata("tiangolo", "fastapi")
            assert metadata["name"] == "fastapi"
            assert metadata["stars"] == 75000
            assert metadata["language"] == "Python"
            assert metadata["default_branch"] == "master"

    async def test_get_repo_metadata_not_found(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_error = True
        mock_response.status_code = 404
        mock_response.text = '{"message": "Not Found"}'
        mock_response.headers = {}

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(GitHubRepositoryNotFoundError, match="not found on GitHub or is private"):
                await gh_service.get_repo_metadata("nonexistent", "repo")

    async def test_get_repo_rate_limit_exceeded(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.is_error = True
        mock_response.status_code = 403
        mock_response.headers = {"x-ratelimit-remaining": "0"}
        mock_response.text = '{"message": "API rate limit exceeded"}'

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(GitHubRateLimitError, match="GitHub API rate limit exceeded"):
                await gh_service.get_repo_metadata("tiangolo", "fastapi")

    async def test_get_readme_success(self, gh_service):
        raw_markdown = "# FastAPI\nHigh performance web framework."
        encoded_content = base64.b64encode(raw_markdown.encode("utf-8")).decode("utf-8")

        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_error = False
        mock_response.json.return_value = {
            "encoding": "base64",
            "content": encoded_content
        }

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            readme = await gh_service.get_readme("tiangolo", "fastapi")
            assert readme == raw_markdown

    async def test_get_readme_missing_returns_none(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_error = True

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            readme = await gh_service.get_readme("tiangolo", "fastapi")
            assert readme is None

    async def test_get_commit_detail_success(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.is_error = False
        mock_response.json.return_value = {
            "sha": "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d",
            "commit": {
                "message": "feat: add response caching\n\nImproves query speed.",
                "author": {"name": "Octocat", "date": "2026-10-15T12:00:00Z"}
            },
            "stats": {"total": 15, "additions": 12, "deletions": 3},
            "files": [
                {
                    "filename": "cache.py",
                    "status": "added",
                    "additions": 12,
                    "deletions": 0,
                    "patch": "@@ -0,0 +1,12 @@\n+def get_cache():\n+    return {}"
                }
            ]
        }

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            commit = await gh_service.get_commit_detail(
                "octocat", "Hello-World", "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"
            )
            assert commit["short_sha"] == "7fd1a60"
            assert "feat: add response caching" in commit["message"]
            assert len(commit["files"]) == 1
            assert "def get_cache" in commit["diff_text"]

    async def test_get_commit_detail_not_found(self, gh_service):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_error = True
        mock_response.headers = {}
        mock_response.text = '{"message": "Not Found"}'

        with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
            with pytest.raises(GitHubCommitNotFoundError, match="Commit not found in repository"):
                await gh_service.get_commit_detail("octocat", "Hello-World", "0000000000")
