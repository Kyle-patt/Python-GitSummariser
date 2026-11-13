"""
Unit tests for OpenAI AI summarization service and structured output generation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from openai import RateLimitError, APITimeoutError

from backend.app.services.ai_service import AIService
from backend.app.schemas.summary import RepoSummaryContent, CommitSummaryContent
from backend.app.core.exceptions import (
    AIConfigurationError,
    AIRateLimitError,
    AITimeoutError,
    AIServiceError,
)


class TestAIService:
    """Test suite for AI summarization logic and prompt structure."""

    def test_missing_api_key_raises_configuration_error(self):
        service = AIService(api_key="")
        with pytest.raises(AIConfigurationError, match="OpenAI API key is missing"):
            service._get_client()

    def test_placeholder_api_key_raises_configuration_error(self):
        service = AIService(api_key="your_openai_api_key_here")
        with pytest.raises(AIConfigurationError, match="OpenAI API key is missing"):
            service._get_client()

    @pytest.mark.asyncio
    async def test_summarize_repository_structured_output_success(self):
        service = AIService(api_key="sk-valid-test-key", model="gpt-4o-mini")

        expected_summary = RepoSummaryContent(
            project_overview="FastAPI is a modern, high-performance web framework for building APIs with Python.",
            key_features=["Fast performance", "Easy to learn", "Automatic interactive docs"],
            prerequisites=["Python 3.8+"],
            beginner_friendly_explanation="Think of FastAPI like an express checkout counter at a supermarket—it handles your requests with minimal delay."
        )

        mock_choice = MagicMock()
        mock_choice.message.refusal = None
        mock_choice.message.parsed = expected_summary

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = AsyncMock()
        mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_response)

        with patch.object(service, "_get_client", return_value=mock_client):
            metadata = {
                "name": "fastapi",
                "full_name": "tiangolo/fastapi",
                "description": "FastAPI framework",
                "language": "Python",
                "stars": 75000,
                "forks": 6000,
                "open_issues": 100,
                "topics": ["fastapi", "python"],
            }
            result = await service.summarize_repository(metadata, "# FastAPI", [])
            assert result.project_overview == expected_summary.project_overview
            assert len(result.key_features) == 3
            assert result.prerequisites == ["Python 3.8+"]
            assert "express checkout" in result.beginner_friendly_explanation

    @pytest.mark.asyncio
    async def test_summarize_commit_structured_output_success(self):
        service = AIService(api_key="sk-valid-test-key", model="gpt-4o-mini")

        expected_commit_summary = CommitSummaryContent(
            concise_summary="Added Redis caching layer to accelerate repository summary lookups.",
            important_features=["Implemented cache invalidation", "Added Redis client integration"],
            bug_fixes=["Fixed race condition during cache population"],
            release_notes="### Release Notes\n\n- **Caching**: Drastically reduced response latency via Redis cache."
        )

        mock_choice = MagicMock()
        mock_choice.message.refusal = None
        mock_choice.message.parsed = expected_commit_summary

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = AsyncMock()
        mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_response)

        with patch.object(service, "_get_client", return_value=mock_client):
            metadata = {"full_name": "owner/repo", "description": "Repo", "language": "Python"}
            commit_detail = {
                "sha": "7fd1a60",
                "message": "feat: add caching",
                "author": "Alice",
                "date": "2026-10-15",
                "files": [],
                "diff_text": "+def cache(): pass"
            }
            result = await service.summarize_commit(metadata, commit_detail)
            assert "Redis caching layer" in result.concise_summary
            assert len(result.bug_fixes) == 1
            assert len(result.important_features) == 2

    @pytest.mark.asyncio
    async def test_ai_rate_limit_maps_to_custom_exception(self):
        service = AIService(api_key="sk-valid-test-key")

        mock_client = AsyncMock()
        mock_client.beta.chat.completions.parse = AsyncMock(
            side_effect=RateLimitError(
                message="Rate limit reached",
                response=MagicMock(status_code=429),
                body=None
            )
        )

        with patch.object(service, "_get_client", return_value=mock_client):
            metadata = {"name": "test", "full_name": "user/test"}
            with pytest.raises(AIRateLimitError, match="OpenAI API rate limit exceeded"):
                await service.summarize_repository(metadata, None, [])

