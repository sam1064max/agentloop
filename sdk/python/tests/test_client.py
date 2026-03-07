import pytest
from agentloop.client import AgentLoopClient
from agentloop.trace import Trace


@pytest.mark.asyncio
async def test_client_track_trace(httpx_mock):
    client = AgentLoopClient(api_key="test_key")
    httpx_mock.add_response(
        method="POST",
        url="https://api.agentloop.dev/v1/traces",
        json={"id": "trace_1", "status": "ok"},
    )
    trace = Trace(session_id="sess_1", prompt="hello", response="world")
    result = await client.track_trace(trace)
    assert result["status"] == "ok"
    await client.close()


@pytest.mark.asyncio
async def test_client_auth_header():
    client = AgentLoopClient(api_key="sk-123")
    assert client._client.headers["Authorization"] == "Bearer sk-123"
    await client.close()


def test_client_defaults():
    client = AgentLoopClient()
    assert client.base_url == "https://api.agentloop.dev"
    assert client.max_retries == 3

# history: test: add SDK client unit tests for Python and TS