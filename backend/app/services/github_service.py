
import re

import httpx
from fastapi import HTTPException


GITHUB_REPO_PATTERN = re.compile(
    r"^https?://github\.com/([^/]+)/([^/]+)/?$",
    re.IGNORECASE,
)


async def get_repository_info(repository_url: str) -> dict:
    match = GITHUB_REPO_PATTERN.fullmatch(repository_url.strip())

    if not match:
        raise HTTPException(
            status_code=400,
            detail="Enter a valid GitHub repository URL.",
        )

    owner, repository = match.groups()
    repository = repository.removesuffix(".git")

    if not owner or not repository:
        raise HTTPException(
            status_code=400,
            detail="Both repository owner and name are required.",
        )

    api_url = (
        f"https://api.github.com/repos/{owner}/{repository}"
    )

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(api_url, headers=headers)

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="GitHub took too long to respond.",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not connect to GitHub.",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail="Repository not found or not publicly accessible.",
        )

    if response.status_code == 403:
        raise HTTPException(
            status_code=502,
            detail="GitHub rate limit or access restriction encountered.",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="GitHub returned an unexpected response.",
        )

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data.get("description"),
        "html_url": data["html_url"],
        "stars": data["stargazers_count"],
        "language": data.get("language"),
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
    }
