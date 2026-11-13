"""
GitHub REST API integration service.
Handles fetching repository metadata, README content, and commit details.
"""
import base64
import logging
from typing import Optional, Dict, Any, List
import httpx

from backend.app.config import settings
from backend.app.core.exceptions import (
    GitHubRepositoryNotFoundError,
    GitHubCommitNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub REST API."""

    def __init__(self, token: Optional[str] = None, timeout: Optional[float] = None):
        self.token = token or settings.GITHUB_TOKEN
        self.timeout = timeout or settings.REQUEST_TIMEOUT_SECONDS
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitSummarizer-Backend/1.0",
        }
        if self.token and self.token.strip() and self.token != "your_github_token_here":
            headers["Authorization"] = f"Bearer {self.token.strip()}"
        return headers

    def _handle_response_error(self, response: httpx.Response, owner: str, repo: str, resource_type: str = "repository"):
        """Maps HTTP error status codes to domain-specific exceptions."""
        status_code = response.status_code

        # Rate limiting check
        if status_code in (403, 429):
            remaining = response.headers.get("x-ratelimit-remaining", "")
            if remaining == "0" or "rate limit" in response.text.lower():
                logger.warning("GitHub API rate limit exceeded.")
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. Set a valid GITHUB_TOKEN in backend environment to increase the rate limit."
                )

        if status_code == 404:
            if resource_type == "commit":
                raise GitHubCommitNotFoundError(
                    f"Commit not found in repository '{owner}/{repo}'. Please check the commit hash."
                )
            raise GitHubRepositoryNotFoundError(
                f"Repository '{owner}/{repo}' not found on GitHub or is private."
            )

        if status_code == 401:
            logger.error("GitHub API 401 Unauthorized with provided token.")
            raise GitHubAPIError("Invalid GitHub API token. Please check your GITHUB_TOKEN configuration.")

        # Raise generic API error for other 4xx/5xx codes
        logger.error(f"GitHub API error {status_code} for {owner}/{repo}: {response.text[:200]}")
        raise GitHubAPIError(f"GitHub API returned unexpected status {status_code}.")

    async def get_repo_metadata(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Fetches repository metadata from GitHub.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                if response.is_error:
                    self._handle_response_error(response, owner, repo, resource_type="repository")
                data = response.json()
        except httpx.TimeoutException:
            logger.error(f"GitHub API timed out while fetching repo metadata for {owner}/{repo}")
            raise GitHubAPIError("Timed out while communicating with GitHub API.")
        except httpx.RequestError as exc:
            logger.error(f"Network error while calling GitHub API: {exc}")
            raise GitHubAPIError(f"Network error while connecting to GitHub: {exc}")

        # Normalize metadata into clean dictionary
        return {
            "name": data.get("name", repo),
            "full_name": data.get("full_name", f"{owner}/{repo}"),
            "description": data.get("description") or "No description provided.",
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "language": data.get("language") or "Not specified",
            "default_branch": data.get("default_branch", "main"),
            "topics": data.get("topics", []),
            "html_url": data.get("html_url", f"https://github.com/{owner}/{repo}"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    async def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Fetches and decodes the README file for a repository.
        Returns None gracefully if the repository does not have a README.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/readme"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)

                # Graceful 404 handling: a repo without a README is valid
                if response.status_code == 404:
                    logger.info(f"Repository {owner}/{repo} does not have a README.")
                    return None

                if response.is_error:
                    self._handle_response_error(response, owner, repo, resource_type="readme")

                data = response.json()
                content_b64 = data.get("content", "")
                encoding = data.get("encoding", "base64")

                if encoding == "base64" and content_b64:
                    decoded_bytes = base64.b64decode(content_b64)
                    readme_text = decoded_bytes.decode("utf-8", errors="replace")
                else:
                    readme_text = content_b64

                # Limit size to prevent token blow-up
                if len(readme_text) > settings.MAX_README_CHARS:
                    readme_text = readme_text[:settings.MAX_README_CHARS] + "\n\n...[README truncated for length]..."

                return readme_text

        except httpx.TimeoutException:
            logger.warning(f"Timeout fetching README for {owner}/{repo}")
            return None
        except httpx.RequestError as exc:
            logger.warning(f"Error fetching README for {owner}/{repo}: {exc}")
            return None

    async def get_recent_commits(self, owner: str, repo: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetches the most recent commits for a repository.
        Returns empty list if repository has no commits.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {"per_page": limit}
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)

                # GitHub returns 409 or 404 if repo is empty
                if response.status_code in (404, 409):
                    logger.info(f"Repository {owner}/{repo} appears to be empty.")
                    return []

                if response.is_error:
                    self._handle_response_error(response, owner, repo, resource_type="commits")

                commits_data = response.json()
                if not isinstance(commits_data, list):
                    return []

                normalized_commits = []
                for item in commits_data:
                    commit_obj = item.get("commit", {})
                    author_obj = commit_obj.get("author", {}) or {}
                    normalized_commits.append({
                        "sha": item.get("sha", "")[:7],
                        "full_sha": item.get("sha", ""),
                        "message": commit_obj.get("message", "").strip(),
                        "author": author_obj.get("name", "Unknown"),
                        "date": author_obj.get("date", ""),
                    })
                return normalized_commits

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning(f"Failed to fetch recent commits for {owner}/{repo}: {exc}")
            return []

    async def get_commit_detail(self, owner: str, repo: str, commit_sha: str) -> Dict[str, Any]:
        """
        Fetches specific commit information including diff patches and changed files.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/commits/{commit_sha}"
        headers = self._get_headers()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                if response.is_error:
                    self._handle_response_error(response, owner, repo, resource_type="commit")
                data = response.json()
        except httpx.TimeoutException:
            logger.error(f"GitHub API timed out fetching commit {commit_sha} for {owner}/{repo}")
            raise GitHubAPIError("Timed out while fetching commit details from GitHub.")
        except httpx.RequestError as exc:
            logger.error(f"Network error fetching commit {commit_sha}: {exc}")
            raise GitHubAPIError(f"Network error connecting to GitHub: {exc}")

        commit_obj = data.get("commit", {})
        author_obj = commit_obj.get("author", {}) or {}
        stats_obj = data.get("stats", {}) or {}

        # Collect changed files and diff patches
        files_data = data.get("files", []) or []
        files_summary = []
        combined_patches = []
        total_patch_chars = 0

        for f in files_data:
            filename = f.get("filename", "")
            status = f.get("status", "modified")
            additions = f.get("additions", 0)
            deletions = f.get("deletions", 0)
            files_summary.append({
                "filename": filename,
                "status": status,
                "additions": additions,
                "deletions": deletions,
            })

            patch = f.get("patch", "")
            if patch and total_patch_chars < settings.MAX_DIFF_CHARS:
                snippet = f"--- {filename} ({status}, +{additions}/-{deletions})\n{patch}\n"
                combined_patches.append(snippet)
                total_patch_chars += len(snippet)

        diff_text = "\n".join(combined_patches)
        if total_patch_chars >= settings.MAX_DIFF_CHARS:
            diff_text += "\n\n...[Diff patches truncated for length]..."

        return {
            "sha": data.get("sha", commit_sha),
            "short_sha": data.get("sha", commit_sha)[:7],
            "message": commit_obj.get("message", "").strip(),
            "author": author_obj.get("name", "Unknown"),
            "date": author_obj.get("date", ""),
            "stats": {
                "total": stats_obj.get("total", 0),
                "additions": stats_obj.get("additions", 0),
                "deletions": stats_obj.get("deletions", 0),
                "changed_files_count": len(files_data),
            },
            "files": files_summary,
            "diff_text": diff_text or "No diff text available.",
        }


# Default singleton instance
github_service = GitHubService()

