"""
Structured output schemas for AI generation and summary response serialization.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict


class RepoSummaryContent(BaseModel):
    """
    Structured AI output for repository analysis.
    Guaranteed schema returned by OpenAI structured generation.
    """
    project_overview: str = Field(
        ...,
        description="A clear, high-level summary of what the project does and the problem it solves."
    )
    key_features: List[str] = Field(
        default_factory=list,
        description="Bullet-point list of the project's primary capabilities and highlights."
    )
    prerequisites: List[str] = Field(
        default_factory=list,
        description="List of tools, runtimes, dependencies, or setup requirements (e.g. Node 18, Python 3.10, Docker)."
    )
    beginner_friendly_explanation: str = Field(
        ...,
        description="An accessible, jargon-free explanation with a relatable analogy for students and junior developers."
    )


class CommitSummaryContent(BaseModel):
    """
    Structured AI output for commit analysis.
    Guaranteed schema returned by OpenAI structured generation.
    """
    concise_summary: str = Field(
        ...,
        description="A 1-2 sentence executive overview of what this commit changes."
    )
    important_features: List[str] = Field(
        default_factory=list,
        description="New functionality or notable improvements introduced by this commit."
    )
    bug_fixes: List[str] = Field(
        default_factory=list,
        description="Bugs or defects resolved in this commit."
    )
    release_notes: str = Field(
        ...,
        description="Clean, user-facing markdown release notes describing the impact of these changes."
    )


class SummaryResponse(BaseModel):
    """API response model for a single summary record."""
    id: str = Field(..., description="Unique record ID")
    repo_url: str = Field(..., description="Full canonical repository URL")
    repo_owner: str = Field(..., description="Repository owner/org")
    repo_name: str = Field(..., description="Repository name")
    commit_sha: Optional[str] = Field(None, description="Commit SHA if this was a commit summary")
    summary_type: str = Field(..., description="'repository' or 'commit'")
    title: str = Field(..., description="Short title describing this summary")
    content: Dict[str, Any] = Field(..., description="Structured summary payload")
    repo_metadata: Optional[Dict[str, Any]] = Field(None, description="Repository metrics (stars, language, etc.)")
    created_at: datetime = Field(..., description="Timestamp when summary was generated")

    model_config = ConfigDict(from_attributes=True)


class HistoryListResponse(BaseModel):
    """API response model for paginated summary history."""
    total: int = Field(..., description="Total number of saved summaries matching criteria")
    items: List[SummaryResponse] = Field(..., description="List of summaries in reverse chronological order")

