"""
Robust GitHub repository and commit URL parsing and validation.
"""
import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from backend.app.core.exceptions import InvalidGitHubURLError

GITHUB_OWNER_REGEX = re.compile(r"^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?$")
GITHUB_REPO_REGEX = re.compile(r"^[a-zA-Z0-9_.-]+$")
COMMIT_SHA_REGEX = re.compile(r"^[0-9a-fA-F]{7,40}$")
ALLOWED_HOSTS = {"github.com", "www.github.com"}


@dataclass(frozen=True)
class ParsedGitHubURL:
    """Structured representation of a validated GitHub URL."""
    raw_url: str
    canonical_url: str
    owner: str
    repo: str
    commit_sha: Optional[str] = None
    is_commit_url: bool = False


def parse_github_url(url: str, expected_commit_sha: Optional[str] = None) -> ParsedGitHubURL:
    """
    Parses and thoroughly validates a GitHub repository or commit URL.

    Handles:
    - Standard repo URLs: https://github.com/owner/repo
    - Trailing slashes: https://github.com/owner/repo/
    - .git extensions: https://github.com/owner/repo.git
    - URLs without scheme: github.com/owner/repo
    - Direct commit URLs: https://github.com/owner/repo/commit/<sha>
    
    Rejects:
    - Non-GitHub hosts (SSRF prevention)
    - Malformed paths and missing owner/repo
    - Invalid commit SHAs
    """
    if not url or not isinstance(url, str) or not url.strip():
        raise InvalidGitHubURLError("Repository URL cannot be empty.")

    cleaned_url = url.strip()

    # Prepend https scheme if missing
    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = f"https://{cleaned_url}"

    try:
        parsed = urlparse(cleaned_url)
    except Exception as exc:
        raise InvalidGitHubURLError(f"Malformed URL: {exc}")

    # Enforce allowed hostnames (prevents SSRF and non-GitHub platforms)
    hostname = (parsed.hostname or "").lower()
    if hostname not in ALLOWED_HOSTS:
        raise InvalidGitHubURLError(
            f"Unsupported host '{hostname}'. Only public GitHub repositories (github.com) are supported."
        )

    # Split and clean path components
    path_segments = [seg for seg in parsed.path.strip("/").split("/") if seg]

    if len(path_segments) < 2:
        raise InvalidGitHubURLError(
            "GitHub URL must include both owner and repository name (e.g., https://github.com/owner/repo)."
        )

    owner = path_segments[0]
    raw_repo = path_segments[1]

    # Validate owner name according to GitHub rules
    if not GITHUB_OWNER_REGEX.match(owner):
        raise InvalidGitHubURLError(
            f"Invalid GitHub username or organization: '{owner}'."
        )

    # Strip .git suffix if present
    repo = raw_repo[:-4] if raw_repo.endswith(".git") else raw_repo

    # Validate repository name
    if not repo or repo in {".", ".."} or not GITHUB_REPO_REGEX.match(repo):
        raise InvalidGitHubURLError(
            f"Invalid GitHub repository name: '{repo}'."
        )

    detected_commit_sha: Optional[str] = None
    is_commit_url = False

    # Check if this is a commit URL: /owner/repo/commit/<sha>
    if len(path_segments) >= 4 and path_segments[2] == "commit":
        detected_commit_sha = path_segments[3]
        is_commit_url = True

    # Allow explicit commit_sha argument to override or populate
    commit_sha = expected_commit_sha or detected_commit_sha

    if commit_sha:
        commit_sha = commit_sha.strip().lower()
        if not COMMIT_SHA_REGEX.match(commit_sha):
            raise InvalidGitHubURLError(
                f"Invalid commit SHA: '{commit_sha}'. Expected 7 to 40 hexadecimal characters."
            )

    canonical_url = f"https://github.com/{owner}/{repo}"

    return ParsedGitHubURL(
        raw_url=url,
        canonical_url=canonical_url,
        owner=owner,
        repo=repo,
        commit_sha=commit_sha,
        is_commit_url=is_commit_url
    )

