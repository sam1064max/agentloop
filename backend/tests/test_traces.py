"""Tests for traces API."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.main import app


@pytest.fixture
def mock_db_session():
    """Create mock database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_trace_data():
    """Sample trace data for testing."""
    return {
        "session_id": "test-session-123",
        "prompt": "What is the capital of France?",
        "response": "The capital of France is Paris.",
        "tool_calls": [
            {
                "tool_name": "search",
                "tool_input": {"query": "capital of France"},
                "tool_output": {"result": "Paris"},
                "success": True,
                "duration_ms": 150.5,
            }
        ],
        "timings": {"total": 250.0, "llm": 200.0},
        "latency_ms": 250.0,
        "cost_usd": 0.002,
    }


@pytest.mark.asyncio
async def test_create_trace(sample_trace_data):
    """Test creating a new trace."""
    with patch("app.api.routes.traces.get_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        mock_get_db.return_value = mock_session

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/traces", json=sample_trace_data)

        assert response.status_code == 201
        data = response.json()
        assert data["prompt"] == sample_trace_data["prompt"]
        assert data["response"] == sample_trace_data["response"]


@pytest.mark.asyncio
async def test_create_trace_with_existing_session(sample_trace_data):
    """Test creating trace with existing session."""
    from app.models.session import Session

    mock_session_obj = Session(
        id=uuid4(),
        session_id=sample_trace_data["session_id"],
        agent_version="v1.0",
        prompt_version="p1.0",
    )

    with patch("app.api.routes.traces.get_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session_obj
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()
        mock_session.flush = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.add = MagicMock()

        mock_get_db.return_value = mock_session

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/traces", json=sample_trace_data)

        assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_trace_not_found():
    """Test getting non-existent trace."""
    trace_id = str(uuid4())

    with patch("app.api.routes.traces.get_db") as mock_get_db:
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value = mock_session

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/traces/{trace_id}")

        assert response.status_code == 404