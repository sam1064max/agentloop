import pytest
from collections import namedtuple

from app.outcome_attributor import (
    OutcomeMetrics,
    AgentVersionMetrics,
    ToolFailureImpact,
    calculate_outcome_metrics,
    compare_agent_versions,
    correlate_tool_failures,
    calculate_prompt_version_metrics,
)

MockSession = namedtuple(
    "MockSession",
    ["session_id", "agent_version", "prompt_version", "path_id", "outcome", "csat_score", "latency_ms", "cost", "tool_failures"]
)


@pytest.fixture
def sample_sessions():
    return [
        MockSession(
            session_id="s1",
            agent_version="v1.0",
            prompt_version="prompt_v1",
            path_id="search_crm_kb_respond",
            outcome="resolved",
            csat_score=5,
            latency_ms=220,
            cost=0.008,
            tool_failures=[],
        ),
        MockSession(
            session_id="s2",
            agent_version="v1.0",
            prompt_version="prompt_v1",
            path_id="search_crm_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=230,
            cost=0.009,
            tool_failures=["crm_lookup"],
        ),
        MockSession(
            session_id="s3",
            agent_version="v1.1",
            prompt_version="prompt_v2",
            path_id="search_kb_respond",
            outcome="escalated",
            csat_score=2,
            latency_ms=160,
            cost=0.006,
            tool_failures=[],
        ),
        MockSession(
            session_id="s4",
            agent_version="v1.1",
            prompt_version="prompt_v2",
            path_id="search_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=170,
            cost=0.006,
            tool_failures=["kb_search"],
        ),
        MockSession(
            session_id="s5",
            agent_version="v2.0",
            prompt_version="prompt_v3",
            path_id="search_escalate",
            outcome="converted",
            csat_score=5,
            latency_ms=120,
            cost=0.004,
            tool_failures=[],
        ),
    ]


class TestCalculateOutcomeMetrics:
    def test_calculate_outcome_metrics_basic(self, sample_sessions):
        metrics = calculate_outcome_metrics(sample_sessions)
        
        assert metrics.total_sessions == 5
        assert metrics.resolution_rate == pytest.approx(0.6, rel=0.01)
        assert metrics.escalation_rate == pytest.approx(0.2, rel=0.01)
        assert metrics.conversion_rate == pytest.approx(0.2, rel=0.01)

    def test_calculate_outcome_metrics_csat(self, sample_sessions):
        metrics = calculate_outcome_metrics(sample_sessions)
        
        expected_avg = (5 + 4 + 2 + 4 + 5) / 5
        assert metrics.csat_avg == pytest.approx(expected_avg, rel=0.01)
        assert metrics.csat_median == 4.0

    def test_calculate_outcome_metrics_empty(self):
        metrics = calculate_outcome_metrics([])
        
        assert metrics.total_sessions == 0
        assert metrics.resolution_rate == 0.0

    def test_calculate_outcome_metrics_to_dict(self, sample_sessions):
        metrics = calculate_outcome_metrics(sample_sessions)
        d = metrics.to_dict()
        
        assert d["total_sessions"] == 5
        assert "resolution_rate" in d
        assert "outcome_counts" in d
        assert d["outcome_counts"]["resolved"] == 3


class TestCompareAgentVersions:
    def test_compare_agent_versions_basic(self, sample_sessions):
        results = compare_agent_versions(sample_sessions)
        
        assert "v1.0" in results
        assert "v1.1" in results
        assert "v2.0" in results

    def test_compare_agent_versions_v1_0_metrics(self, sample_sessions):
        results = compare_agent_versions(sample_sessions)
        
        v1_0 = results["v1.0"]
        assert v1_0.total_sessions == 2
        assert v1_0.version == "v1.0"
        assert v1_0.resolution_rate == 1.0

    def test_compare_agent_versions_v1_1_metrics(self, sample_sessions):
        results = compare_agent_versions(sample_sessions)
        
        v1_1 = results["v1.1"]
        assert v1_1.total_sessions == 2
        assert v1_1.escalation_rate == 0.5

    def test_compare_agent_versions_empty(self):
        results = compare_agent_versions([])
        assert results == {}

    def test_compare_agent_versions_to_dict(self, sample_sessions):
        results = compare_agent_versions(sample_sessions)
        d = results["v1.0"].to_dict()
        
        assert d["version"] == "v1.0"
        assert d["total_sessions"] == 2
        assert "resolution_rate" in d


class TestCorrelateToolFailures:
    def test_correlate_tool_failures_basic(self, sample_sessions):
        results = correlate_tool_failures(sample_sessions)
        
        assert len(results) > 0
        assert all(isinstance(r, ToolFailureImpact) for r in results)

    def test_correlate_tool_failures_counts(self, sample_sessions):
        results = correlate_tool_failures(sample_sessions)
        result_dict = {r.tool_name: r for r in results}
        
        assert "crm_lookup" in result_dict
        assert result_dict["crm_lookup"].failure_count == 1

    def test_correlate_tool_failures_empty(self):
        results = correlate_tool_failures([])
        assert results == []

    def test_correlate_tool_failures_with_string_failures(self, sample_sessions):
        class SessionWithStringFailures:
            def __init__(self, failures_str):
                self.tool_failures = failures_str
                self.csat_score = 3
                self.latency_ms = 200
                self.outcome = "resolved"
        
        sessions = [
            SessionWithStringFailures("search,crm_lookup"),
            SessionWithStringFailures(""),
        ]
        results = correlate_tool_failures(sessions)
        assert len(results) >= 0


class TestCalculatePromptVersionMetrics:
    def test_prompt_version_metrics(self, sample_sessions):
        results = calculate_prompt_version_metrics(sample_sessions)
        
        assert "prompt_v1" in results
        assert "prompt_v2" in results
        assert results["prompt_v1"].resolution_rate == 1.0
        assert results["prompt_v2"].resolution_rate == 0.5

    def test_prompt_version_metrics_empty(self):
        results = calculate_prompt_version_metrics([])
        assert results == {}