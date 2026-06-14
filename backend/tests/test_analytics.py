"""Tests for analytics API."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.models.session import Session
from app.models.trace import Trace
from app.models.outcome import Outcome
from app.models.feedback import Feedback
from app.services.analytics_service import AnalyticsService


@pytest.fixture
def sample_sessions():
    """Create sample sessions."""
    sessions = []
    for i in range(5):
        session = MagicMock()
        session.id = uuid4()
        session.session_id = f"session-{i}"
        session.agent_version = f"v1.{i % 2}"
        session.prompt_version = "p1.0"
        session.created_at = datetime.now(timezone.utc)
        sessions.append(session)
    return sessions


@pytest.fixture
def sample_traces(sample_sessions):
    """Create sample traces."""
    traces = []
    for session in sample_sessions:
        trace = MagicMock()
        trace.id = uuid4()
        trace.session_id = session.id
        trace.prompt = "Test prompt"
        trace.response = "Test response"
        trace.tool_calls_json = [
            {"tool_name": "search", "success": True},
            {"tool_name": "fetch", "success": True},
        ]
        trace.latency_ms = 200.0
        trace.cost_usd = 0.01
        trace.created_at = datetime.now(timezone.utc)
        traces.append(trace)
    return traces


@pytest.fixture
def sample_outcomes(sample_sessions):
    """Create sample outcomes."""
    outcomes = []
    for i, session in enumerate(sample_sessions):
        outcome = MagicMock()
        outcome.id = uuid4()
        outcome.session_id = session.id
        outcome.outcome_type = ["resolved", "escalated", "converted"][i % 3]
        outcome.value = 100.0
        outcome.created_at = datetime.now(timezone.utc)
        outcomes.append(outcome)
    return outcomes


@pytest.fixture
def sample_feedbacks(sample_sessions):
    """Create sample feedbacks."""
    feedbacks = []
    for i, session in enumerate(sample_sessions):
        feedback = MagicMock()
        feedback.id = uuid4()
        feedback.session_id = session.id
        feedback.rating = (i % 5) + 1
        feedback.comment = f"Feedback {i}"
        feedback.tags = ["test"]
        feedback.created_at = datetime.now(timezone.utc)
        feedbacks.append(feedback)
    return feedbacks


class TestAnalyticsService:
    """Tests for AnalyticsService."""

    def test_calculate_path_success(self, sample_sessions, sample_traces):
        """Test path success calculation."""
        service = AnalyticsService()
        result = service.calculate_path_success(sample_sessions, sample_traces)

        assert isinstance(result, list)
        for path_analysis in result:
            assert hasattr(path_analysis, "path")
            assert hasattr(path_analysis, "total_sessions")
            assert hasattr(path_analysis, "success_rate")

    def test_calculate_outcome_metrics(
        self, sample_sessions, sample_feedbacks, sample_outcomes
    ):
        """Test outcome metrics calculation."""
        service = AnalyticsService()
        result = service.calculate_outcome_metrics(
            sample_sessions, sample_feedbacks, sample_outcomes
        )

        assert result is not None
        assert result.total_sessions == len(sample_sessions)
        assert result.resolved_count >= 0
        assert result.escalated_count >= 0
        assert 0 <= result.resolution_rate <= 1
        assert 0 <= result.escalation_rate <= 1

    def test_calculate_agent_comparison(
        self, sample_sessions, sample_traces, sample_feedbacks, sample_outcomes
    ):
        """Test agent version comparison."""
        service = AnalyticsService()
        result = service.calculate_agent_comparison(
            sample_sessions, sample_traces, sample_feedbacks, sample_outcomes
        )

        assert isinstance(result, list)
        for comparison in result:
            assert hasattr(comparison, "agent_version")
            assert hasattr(comparison, "session_count")
            assert hasattr(comparison, "success_rate")

    def test_generate_root_cause_insights(
        self, sample_sessions, sample_traces, sample_outcomes
    ):
        """Test root cause insight generation."""
        service = AnalyticsService()
        result = service.generate_root_cause_insights(
            sample_sessions, sample_traces, sample_outcomes
        )

        assert isinstance(result, list)
        for insight in result:
            assert hasattr(insight, "insight_type")
            assert hasattr(insight, "description")
            assert hasattr(insight, "impact_score")

    def test_generate_recommendations(self, sample_sessions, sample_traces, sample_outcomes):
        """Test recommendation generation."""
        service = AnalyticsService()
        insights = service.generate_root_cause_insights(
            sample_sessions, sample_traces, sample_outcomes
        )
        result = service.generate_recommendations(insights)

        assert isinstance(result, list)
        for recommendation in result:
            assert hasattr(recommendation, "recommendation_type")
            assert hasattr(recommendation, "title")
            assert hasattr(recommendation, "priority")

    def test_calculate_outcome_metrics_empty_sessions(self):
        """Test outcome metrics with empty sessions."""
        service = AnalyticsService()
        result = service.calculate_outcome_metrics([], [], [])

        assert result is None


@pytest.mark.asyncio
async def test_get_analytics_endpoint():
    """Test analytics endpoint returns proper structure."""
    with patch("app.api.routes.analytics.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
        mock_get_db.return_value = mock_db

        from app.main import app
        from httpx import AsyncClient, ASGITransport

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get("/api/v1/analytics")

        assert response.status_code == 200
        data = response.json()
        assert "path_analysis" in data
        assert "outcome_metrics" in data
        assert "agent_comparison" in data
        assert "root_cause_insights" in data
        assert "recommendations" in data
        assert "generated_at" in data