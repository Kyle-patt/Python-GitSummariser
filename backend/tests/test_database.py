"""
Unit tests for database models, persistence, and queries.
"""
from datetime import datetime, timezone
from backend.app.models.summary import SummaryRecord


class TestDatabaseModels:
    """Test suite for SQLite and SQLAlchemy persistence."""

    def test_create_and_retrieve_summary_record(self, db_session):
        record = SummaryRecord(
            repo_url="https://github.com/facebook/react",
            repo_owner="facebook",
            repo_name="react",
            commit_sha=None,
            summary_type="repository",
            title="facebook/react Overview",
            content={
                "project_overview": "A JavaScript library for building user interfaces.",
                "key_features": ["Declarative", "Component-Based", "Learn Once, Write Anywhere"],
                "prerequisites": ["Node.js 18+"],
                "beginner_friendly_explanation": "React is like Lego blocks for building websites."
            },
            repo_metadata={"stars": 220000, "language": "JavaScript"},
            created_at=datetime.now(timezone.utc)
        )
        db_session.add(record)
        db_session.commit()

        # Retrieve
        fetched = db_session.query(SummaryRecord).filter(SummaryRecord.id == record.id).first()
        assert fetched is not None
        assert fetched.repo_name == "react"
        assert fetched.repo_owner == "facebook"
        assert fetched.content["key_features"][0] == "Declarative"
        assert fetched.summary_type == "repository"

    def test_filter_by_summary_type(self, db_session):
        rec1 = SummaryRecord(
            repo_url="https://github.com/a/b",
            repo_owner="a",
            repo_name="b",
            summary_type="repository",
            title="Repo Summary",
            content={"overview": "Test"}
        )
        rec2 = SummaryRecord(
            repo_url="https://github.com/a/b",
            repo_owner="a",
            repo_name="b",
            commit_sha="abcdef1",
            summary_type="commit",
            title="Commit Summary",
            content={"overview": "Test"}
        )
        db_session.add_all([rec1, rec2])
        db_session.commit()

        commit_records = db_session.query(SummaryRecord).filter(SummaryRecord.summary_type == "commit").all()
        assert len(commit_records) == 1
        assert commit_records[0].commit_sha == "abcdef1"

    def test_delete_summary_record(self, db_session):
        rec = SummaryRecord(
            repo_url="https://github.com/test/repo",
            repo_owner="test",
            repo_name="repo",
            summary_type="repository",
            title="To Delete",
            content={"overview": "Temporary"}
        )
        db_session.add(rec)
        db_session.commit()

        rec_id = rec.id
        db_session.delete(rec)
        db_session.commit()

        assert db_session.query(SummaryRecord).filter(SummaryRecord.id == rec_id).first() is None

