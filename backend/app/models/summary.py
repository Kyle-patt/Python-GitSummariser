"""
SQLAlchemy ORM models for saved repository summaries and search history.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.app.database import Base


class SummaryRecord(Base):
    """
    Persisted record of repository overview or commit release notes.
    """
    __tablename__ = "summary_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    repo_url = Column(String(500), nullable=False)
    repo_owner = Column(String(100), nullable=False, index=True)
    repo_name = Column(String(100), nullable=False, index=True)
    commit_sha = Column(String(40), nullable=True, index=True)
    summary_type = Column(String(20), nullable=False, index=True)  # "repository" | "commit"
    title = Column(String(255), nullable=False)
    content = Column(JSON, nullable=False)  # Stores the structured summary dict
    repo_metadata = Column(JSON, nullable=True)  # Stars, forks, language, etc.
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    def to_dict(self) -> dict:
        """Helper to convert model to dictionary representation."""
        return {
            "id": self.id,
            "repo_url": self.repo_url,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "commit_sha": self.commit_sha,
            "summary_type": self.summary_type,
            "title": self.title,
            "content": self.content,
            "repo_metadata": self.repo_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

