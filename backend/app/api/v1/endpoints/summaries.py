"""
API endpoints for initiating repository overviews and commit release notes summaries.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.schemas.request import RepoSummaryRequest, CommitSummaryRequest
from backend.app.schemas.summary import SummaryResponse
from backend.app.services.orchestrator import orchestrator

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post(
    "/repository",
    response_model=SummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Repository Summary",
    description="Accepts a public GitHub repository URL, fetches its metadata/README/commits, and produces a structured beginner-friendly overview."
)
async def create_repository_summary(
    payload: RepoSummaryRequest,
    db: Session = Depends(get_db)
):
    record = await orchestrator.summarize_repository(db=db, repo_url=payload.repo_url)
    return record


@router.post(
    "/commit",
    response_model=SummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Commit Release Notes",
    description="Accepts a GitHub repository URL and commit SHA (or commit URL), fetches diffs and changes, and produces clean structured release notes."
)
async def create_commit_summary(
    payload: CommitSummaryRequest,
    db: Session = Depends(get_db)
):
    record = await orchestrator.summarize_commit(
        db=db,
        repo_url=payload.repo_url,
        commit_sha=payload.commit_sha
    )
    return record

