import asyncio
from typing import Any, Dict, List, Optional
import httpx
from .trace import Trace
from .outcome import Outcome
from .feedback import Feedback
from .experiment import Experiment
from .version import Version


class AgentLoopClient:
    def __init__(
        self,
        base_url: str = "https://api.agentloop.dev",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(timeout),
        )

    async def _request(self, method: str, path: str, json_data: Any = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        for attempt in range(self.max_retries):
            try:
                response = await self._client.request(method, url, json=json_data)
                response.raise_for_status()
                return response.json()
            except (httpx.RequestError, httpx.HTTPStatusError) as exc:
                if attempt == self.max_retries - 1:
                    raise
                delay = 1.0 * (2 ** attempt)
                await asyncio.sleep(delay)

    async def track_trace(self, trace: Trace) -> Dict[str, Any]:
        return await self._request("POST", "/v1/traces", json_data=trace.to_dict())

    async def track_outcome(self, outcome: Outcome) -> Dict[str, Any]:
        return await self._request("POST", "/v1/outcomes", json_data=outcome.to_dict())

    async def track_feedback(self, feedback: Feedback) -> Dict[str, Any]:
        return await self._request("POST", "/v1/feedback", json_data=feedback.to_dict())

    async def track_experiment(self, experiment: Experiment) -> Dict[str, Any]:
        return await self._request("POST", "/v1/experiments", json_data=experiment.to_dict())

    async def track_version(self, version: Version) -> Dict[str, Any]:
        return await self._request("POST", "/v1/versions", json_data=version.to_dict())

    async def track_traces_batch(self, traces: List[Trace]) -> Dict[str, Any]:
        return await self._request("POST", "/v1/traces/batch", json_data=[t.to_dict() for t in traces])

    async def track_outcomes_batch(self, outcomes: List[Outcome]) -> Dict[str, Any]:
        return await self._request("POST", "/v1/outcomes/batch", json_data=[o.to_dict() for o in outcomes])

    async def close(self) -> None:
        await self._client.aclose()

# history: feat: implement Python SDK client with session API