"""
Unit tests for GitHub URL parsing, normalization, and validation.
"""
import pytest
from backend.app.utils.url_parser import parse_github_url, ParsedGitHubURL
from backend.app.core.exceptions import InvalidGitHubURLError


class TestURLParser:
    """Test suite for URL parsing edge cases and security protections."""

    def test_valid_standard_repo_url(self):
        url = "https://github.com/fastapi/fastapi"
        parsed = parse_github_url(url)
        assert parsed.owner == "fastapi"
        assert parsed.repo == "fastapi"
        assert parsed.canonical_url == "https://github.com/fastapi/fastapi"
        assert parsed.commit_sha is None
        assert parsed.is_commit_url is False

    def test_valid_url_with_trailing_slash(self):
        url = "https://github.com/torvalds/linux/"
        parsed = parse_github_url(url)
        assert parsed.owner == "torvalds"
        assert parsed.repo == "linux"
        assert parsed.canonical_url == "https://github.com/torvalds/linux"

    def test_valid_url_with_git_extension(self):
        url = "https://github.com/psf/requests.git"
        parsed = parse_github_url(url)
        assert parsed.owner == "psf"
        assert parsed.repo == "requests"
        assert parsed.canonical_url == "https://github.com/psf/requests"

    def test_valid_url_without_scheme(self):
        url = "github.com/django/django"
        parsed = parse_github_url(url)
        assert parsed.owner == "django"
        assert parsed.repo == "django"
        assert parsed.canonical_url == "https://github.com/django/django"

    def test_valid_commit_url(self):
        sha = "7fd1a60b01f91b314f59955a4e4d4e80d8dee11d"
        url = f"https://github.com/octocat/Hello-World/commit/{sha}"
        parsed = parse_github_url(url)
        assert parsed.owner == "octocat"
        assert parsed.repo == "Hello-World"
        assert parsed.commit_sha == sha
        assert parsed.is_commit_url is True
        assert parsed.canonical_url == "https://github.com/octocat/Hello-World"

    def test_valid_short_commit_sha_override(self):
        url = "https://github.com/octocat/Hello-World"
        parsed = parse_github_url(url, expected_commit_sha="7fd1a60")
        assert parsed.commit_sha == "7fd1a60"

    def test_reject_empty_or_whitespace_url(self):
        with pytest.raises(InvalidGitHubURLError, match="cannot be empty"):
            parse_github_url("   ")

    def test_reject_unsupported_host_ssrf_prevention(self):
        unsupported = [
            "https://gitlab.com/owner/repo",
            "https://bitbucket.org/owner/repo",
            "http://localhost:8000/owner/repo",
            "http://169.254.169.254/latest/meta-data",
            "https://evil-github.com/owner/repo",
        ]
        for url in unsupported:
            with pytest.raises(InvalidGitHubURLError, match="Unsupported host"):
                parse_github_url(url)

    def test_reject_missing_repository(self):
        with pytest.raises(InvalidGitHubURLError, match="must include both owner and repository"):
            parse_github_url("https://github.com/fastapi")

    def test_reject_invalid_owner_names(self):
        invalid_owners = [
            "https://github.com/-fastapi/fastapi",
            "https://github.com/fastapi-/fastapi",
            "https://github.com/fast api/fastapi",
        ]
        for url in invalid_owners:
            with pytest.raises(InvalidGitHubURLError, match="Invalid GitHub username"):
                parse_github_url(url)

    def test_reject_invalid_repo_names(self):
        invalid_repos = [
            "https://github.com/fastapi/.",
            "https://github.com/fastapi/..",
            "https://github.com/fastapi/.git",
        ]
        for url in invalid_repos:
            with pytest.raises(InvalidGitHubURLError, match="Invalid GitHub repository name"):
                parse_github_url(url)

    def test_reject_malformed_commit_sha(self):
        with pytest.raises(InvalidGitHubURLError, match="Invalid commit SHA"):
            parse_github_url("https://github.com/owner/repo/commit/not-a-hex-sha")

        with pytest.raises(InvalidGitHubURLError, match="Invalid commit SHA"):
            parse_github_url("https://github.com/owner/repo/commit/123")  # too short

