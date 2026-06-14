"""Tests for feedback API."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.main import app
from app.models.session import Session


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing."""
    return {
        "session_id": "test-session-123",
        "rating": 5,
        "comment": "Great response!",
        "tags": ["helpful", "accurate"],
    }


@pytest.fixture
def mock_session():
    """Create mock session object."""
    session = Session(
        id=uuid4(),
        session_id="test-session-123",
        agent_version="v1.0",
        prompt_version="p1.0",
    )
    return session


@pytest.mark.asyncio
async def test_create_feedback_success(sample_feedback_data, mock_session):
    """Test successful feedback creation."""
    with patch("app.api.routes.feedback.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_session
        mock_db.execute = AsyncMock(return_value=mock_result)
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.add = MagicMock()

        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/feedback", json=sample_feedback_data)

        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == sample_feedback_data["rating"]
        assert data["comment"] == sample_feedback_data["comment"]


@pytest.mark.asyncio
async def test_create_feedback_session_not_found(sample_feedback_data):
    """Test feedback creation with non-existent session."""
    with patch("app.api.routes.feedback.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/feedback", json=sample_feedback_data)

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_feedback_invalid_rating(mock_session):
    """Test feedback creation with invalid rating."""
    invalid_data = {
        "session_id": "test-session-123",
        "rating": 6,
        "comment": "Test",
    }

    with patch("app.api.routes.feedback.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/feedback", json=invalid_data)

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_feedback_not_found():
    """Test getting non-existent feedback."""
    feedback_id = str(uuid4())

    with patch("app.api.routes.feedback.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/feedback/{feedback_id}")

        assert response.status_code == 404