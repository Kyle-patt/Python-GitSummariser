"""
Pydantic input validation schemas for repository and commit summarization requests.
"""
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from backend.app.utils.url_parser import parse_github_url
from backend.app.core.exceptions import InvalidGitHubURLError


class RepoSummaryRequest(BaseModel):
    """Payload for generating a repository overview."""
    repo_url: str = Field(
        ...,
        description="Public GitHub repository URL (e.g. https://github.com/fastapi/fastapi)",
        examples=["https://github.com/psf/requests"]
    )

    @model_validator(mode="after")
    def validate_url(self) -> "RepoSummaryRequest":
        # Raises InvalidGitHubURLError if URL format, domain, or owner/repo is invalid
        parse_github_url(self.repo_url)
        return self


class CommitSummaryRequest(BaseModel):
    """Payload for generating release notes from a commit."""
    repo_url: str = Field(
        ...,
        description="GitHub repository URL or direct commit URL",
        examples=["https://github.com/psf/requests"]
    )
    commit_sha: Optional[str] = Field(
        None,
        description="Commit hash (7-40 hex characters). Optional if embedded in repo_url.",
        examples=["7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"]
    )

    @model_validator(mode="after")
    def validate_commit_info(self) -> "CommitSummaryRequest":
        parsed = parse_github_url(self.repo_url, expected_commit_sha=self.commit_sha)
        if not parsed.commit_sha:
            raise InvalidGitHubURLError(
                "A valid commit SHA must be provided either in the URL (https://github.com/owner/repo/commit/<sha>) or via the commit_sha field."
            )
        # Canonicalize commit SHA to lowercase
        self.commit_sha = parsed.commit_sha
        return self

