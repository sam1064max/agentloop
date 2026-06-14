"""Tests for outcomes API."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.main import app
from app.models.session import Session


@pytest.fixture
def sample_outcome_data():
    """Sample outcome data for testing."""
    return {
        "session_id": "test-session-123",
        "outcome_type": "resolved",
        "value": 100.0,
        "metadata": {"resolution_time_ms": 5000},
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
async def test_create_outcome_success(sample_outcome_data, mock_session):
    """Test successful outcome creation."""
    with patch("app.api.routes.outcomes.get_db") as mock_get_db:
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
            response = await client.post("/api/v1/outcomes", json=sample_outcome_data)

        assert response.status_code == 201
        data = response.json()
        assert data["outcome_type"] == sample_outcome_data["outcome_type"]
        assert data["value"] == sample_outcome_data["value"]


@pytest.mark.asyncio
async def test_create_outcome_session_not_found(sample_outcome_data):
    """Test outcome creation with non-existent session."""
    with patch("app.api.routes.outcomes.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/outcomes", json=sample_outcome_data)

        assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_outcome_invalid_type(mock_session):
    """Test outcome creation with invalid outcome type."""
    invalid_data = {
        "session_id": "test-session-123",
        "outcome_type": "invalid_type",
        "value": 100.0,
    }

    with patch("app.api.routes.outcomes.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.post("/api/v1/outcomes", json=invalid_data)

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_outcome_not_found():
    """Test getting non-existent outcome."""
    outcome_id = str(uuid4())

    with patch("app.api.routes.outcomes.get_db") as mock_get_db:
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)

        mock_get_db.return_value = mock_db

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
        ) as client:
            response = await client.get(f"/api/v1/outcomes/{outcome_id}")

        assert response.status_code == 404