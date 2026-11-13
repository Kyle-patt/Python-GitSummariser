"""
Orchestration layer coordinating URL parsing, GitHub data fetching,
AI structured summarization, and database persistence.
"""
import asyncio
import logging
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.models.summary import SummaryRecord
from backend.app.services.github_service import github_service, GitHubService
from backend.app.services.ai_service import ai_service, AIService
from backend.app.utils.url_parser import parse_github_url, ParsedGitHubURL

logger = logging.getLogger(__name__)


class SummaryOrchestrator:
    """Coordinates end-to-end repository and commit summarization pipelines."""

    def __init__(self, gh_service: Optional[GitHubService] = None, llm_service: Optional[AIService] = None):
        self.github = gh_service or github_service
        self.ai = llm_service or ai_service

    async def summarize_repository(self, db: Session, repo_url: str) -> SummaryRecord:
        """
        Full pipeline for repository summarization:
        1. Parse and validate GitHub URL.
        2. Fetch metadata, README, and recent commits via GitHub REST API.
        3. Pass normalized context to AI service for structured output.
        4. Persist result in database.
        5. Return the created SummaryRecord.
        """
        # Step 1: Parse and validate URL
        parsed: ParsedGitHubURL = parse_github_url(repo_url)
        owner, repo = parsed.owner, parsed.repo

        logger.info(f"Initiating repository summarization for {owner}/{repo}")

        # Step 2: Fetch GitHub repository data
        # Fetch metadata first to ensure repo exists before fetching README/commits
        metadata = await self.github.get_repo_metadata(owner, repo)

        # Concurrently fetch README and recent commit logs
        readme, recent_commits = await asyncio.gather(
            self.github.get_readme(owner, repo),
            self.github.get_recent_commits(owner, repo, limit=5)
        )

        logger.info(f"Successfully fetched GitHub data for {owner}/{repo}. Triggering AI analysis.")

        # Step 3: Run AI structured generation
        ai_summary = await self.ai.summarize_repository(
            metadata=metadata,
            readme=readme,
            recent_commits=recent_commits
        )

        # Step 4: Persist summary into database
        summary_record = SummaryRecord(
            repo_url=parsed.canonical_url,
            repo_owner=owner,
            repo_name=repo,
            commit_sha=None,
            summary_type="repository",
            title=f"{owner}/{repo} Overview",
            content=ai_summary.model_dump(),
            repo_metadata=metadata,
        )

        db.add(summary_record)
        db.commit()
        db.refresh(summary_record)

        logger.info(f"Successfully persisted repository summary (ID: {summary_record.id})")
        return summary_record

    async def summarize_commit(self, db: Session, repo_url: str, commit_sha: Optional[str] = None) -> SummaryRecord:
        """
        Full pipeline for commit summarization:
        1. Parse and validate GitHub repo URL & commit SHA.
        2. Fetch repository metadata and commit details/diffs via GitHub REST API.
        3. Pass normalized context to AI service for release notes generation.
        4. Persist result in database.
        5. Return the created SummaryRecord.
        """
        # Step 1: Parse and validate URL and commit SHA
        parsed: ParsedGitHubURL = parse_github_url(repo_url, expected_commit_sha=commit_sha)
        owner, repo = parsed.owner, parsed.repo
        target_sha = parsed.commit_sha

        logger.info(f"Initiating commit summarization for {owner}/{repo} @ {target_sha}")

        # Step 2: Fetch repo metadata and commit details with diff
        metadata = await self.github.get_repo_metadata(owner, repo)
        commit_detail = await self.github.get_commit_detail(owner, repo, target_sha)

        logger.info(f"Successfully fetched commit data for {owner}/{repo} @ {target_sha}. Triggering AI analysis.")

        # Step 3: Run AI structured generation
        ai_release_notes = await self.ai.summarize_commit(
            metadata=metadata,
            commit_detail=commit_detail
        )

        # Step 4: Persist summary into database
        summary_record = SummaryRecord(
            repo_url=parsed.canonical_url,
            repo_owner=owner,
            repo_name=repo,
            commit_sha=target_sha,
            summary_type="commit",
            title=f"Release Notes: {owner}/{repo} ({target_sha[:7]})",
            content=ai_release_notes.model_dump(),
            repo_metadata=metadata,
        )

        db.add(summary_record)
        db.commit()
        db.refresh(summary_record)

        logger.info(f"Successfully persisted commit summary (ID: {summary_record.id})")
        return summary_record


# Default singleton instance
orchestrator = SummaryOrchestrator()

