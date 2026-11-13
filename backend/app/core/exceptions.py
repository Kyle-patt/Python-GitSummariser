"""
Core custom domain exceptions for GitSummarizer backend.
"""
from typing import Optional, Any


class GitSummarizerException(Exception):
    """Base exception for application domain errors."""
    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


class InvalidGitHubURLError(GitSummarizerException):
    """Raised when user provides an invalid, malformed, or untrusted GitHub URL."""
    def __init__(self, message: str = "Invalid GitHub repository URL."):
        super().__init__(message=message, status_code=422)


class GitHubRepositoryNotFoundError(GitSummarizerException):
    """Raised when the requested repository is not found or is private."""
    def __init__(self, message: str = "GitHub repository not found or is inaccessible."):
        super().__init__(message=message, status_code=404)


class GitHubCommitNotFoundError(GitSummarizerException):
    """Raised when the specified commit SHA cannot be found in the repository."""
    def __init__(self, message: str = "Specified commit was not found in the repository."):
        super().__init__(message=message, status_code=404)


class GitHubRateLimitError(GitSummarizerException):
    """Raised when GitHub REST API rate limits are exceeded."""
    def __init__(self, message: str = "GitHub API rate limit exceeded. Please configure GITHUB_TOKEN or try again later."):
        super().__init__(message=message, status_code=429)


class GitHubAPIError(GitSummarizerException):
    """Raised when GitHub REST API returns an unexpected error or times out."""
    def __init__(self, message: str = "Failed to communicate with GitHub API."):
        super().__init__(message=message, status_code=502)


class AIConfigurationError(GitSummarizerException):
    """Raised when AI provider API key or required model settings are missing."""
    def __init__(self, message: str = "AI service is not configured. Please set OPENAI_API_KEY in the backend environment."):
        super().__init__(message=message, status_code=503)


class AIRateLimitError(GitSummarizerException):
    """Raised when the AI provider rate limits the requests."""
    def __init__(self, message: str = "AI service rate limit reached. Please retry in a moment."):
        super().__init__(message=message, status_code=429)


class AITimeoutError(GitSummarizerException):
    """Raised when AI provider inference times out."""
    def __init__(self, message: str = "AI generation request timed out."):
        super().__init__(message=message, status_code=504)


class AIServiceError(GitSummarizerException):
    """Raised when AI provider fails to produce a valid response."""
    def __init__(self, message: str = "AI service failed to generate summary."):
        super().__init__(message=message, status_code=502)


class SummaryNotFoundError(GitSummarizerException):
    """Raised when a summary history record does not exist in the database."""
    def __init__(self, message: str = "Summary record not found."):
        super().__init__(message=message, status_code=404)

