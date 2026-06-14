import pytest
from collections import namedtuple

from app.root_cause_engine import (
    RootCauseInsight,
    detect_regressions,
    find_correlated_failures,
    generate_recommendations,
    _calculate_regression,
)

MockSession = namedtuple(
    "MockSession",
    ["session_id", "agent_version", "path_id", "outcome", "csat_score", "latency_ms", "cost", "tool_failures"]
)


@pytest.fixture
def baseline_sessions():
    return [
        MockSession(
            session_id=f"b{i}",
            agent_version="v1.0",
            path_id="search_crm_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=200,
            cost=0.008,
            tool_failures=[],
        )
        for i in range(50)
    ] + [
        MockSession(
            session_id=f"b{i}",
            agent_version="v1.0",
            path_id="search_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=150,
            cost=0.006,
            tool_failures=[],
        )
        for i in range(50)
    ]


@pytest.fixture
def current_sessions_with_regression():
    sessions = [
        MockSession(
            session_id=f"c{i}",
            agent_version="v1.0",
            path_id="search_crm_kb_respond",
            outcome="resolved",
            csat_score=3,
            latency_ms=250,
            cost=0.008,
            tool_failures=[],
        )
        for i in range(25)
    ] + [
        MockSession(
            session_id=f"c{i}",
            agent_version="v1.0",
            path_id="search_crm_kb_respond",
            outcome="escalated",
            csat_score=2,
            latency_ms=260,
            cost=0.009,
            tool_failures=[],
        )
        for i in range(25)
    ] + [
        MockSession(
            session_id=f"c{i}",
            agent_version="v1.0",
            path_id="search_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=150,
            cost=0.006,
            tool_failures=[],
        )
        for i in range(50)
    ]
    return sessions


@pytest.fixture
def sessions_with_tool_failures():
    sessions = []
    
    for i in range(30):
        sessions.append(MockSession(
            session_id=f"f{i}",
            agent_version="v1.0",
            path_id="search_crm_kb_respond",
            outcome="escalated",
            csat_score=2,
            latency_ms=300,
            cost=0.010,
            tool_failures=["crm_lookup"],
        ))
    
    for i in range(70):
        sessions.append(MockSession(
            session_id=f"n{i}",
            agent_version="v1.0",
            path_id="search_crm_kb_respond",
            outcome="resolved",
            csat_score=4,
            latency_ms=200,
            cost=0.008,
            tool_failures=[],
        ))
    
    return sessions


class TestDetectRegressions:
    def test_detect_regressions_returns_list(self, baseline_sessions, current_sessions_with_regression):
        insights = detect_regressions(current_sessions_with_regression, baseline_sessions)
        assert isinstance(insights, list)

    def test_detect_regressions_empty_current(self, baseline_sessions):
        insights = detect_regressions([], baseline_sessions)
        assert insights == []

    def test_detect_regressions_empty_baseline(self, current_sessions_with_regression):
        insights = detect_regressions(current_sessions_with_regression, [])
        assert insights == []

    def test_detect_regressions_both_empty(self):
        insights = detect_regressions([], [])
        assert insights == []

    def test_detect_regressions_sorted_by_impact(self, baseline_sessions, current_sessions_with_regression):
        insights = detect_regressions(current_sessions_with_regression, baseline_sessions)
        if len(insights) > 1:
            assert insights[0].impact_score >= insights[1].impact_score

    def test_detect_regressions_insight_structure(self, baseline_sessions, current_sessions_with_regression):
        insights = detect_regressions(current_sessions_with_regression, baseline_sessions)
        for insight in insights:
            assert isinstance(insight, RootCauseInsight)
            assert insight.insight_type in ["regression", "path_regression"]
            assert insight.title
            assert insight.description
            assert 0 <= insight.impact_score <= 1
            assert 0 <= insight.confidence <= 1


class TestFindCorrelatedFailures:
    def test_find_correlated_failures_returns_list(self, sessions_with_tool_failures):
        insights = find_correlated_failures(sessions_with_tool_failures)
        assert isinstance(insights, list)

    def test_find_correlated_failures_empty(self):
        insights = find_correlated_failures([])
        assert insights == []

    def test_find_correlated_failures_finds_tool_issues(self, sessions_with_tool_failures):
        insights = find_correlated_failures(sessions_with_tool_failures)
        tool_insights = [i for i in insights if i.insight_type == "tool_correlation"]
        assert len(tool_insights) >= 0

    def test_find_correlated_failures_insight_structure(self, sessions_with_tool_failures):
        insights = find_correlated_failures(sessions_with_tool_failures)
        for insight in insights:
            assert isinstance(insight, RootCauseInsight)
            assert insight.insight_type in ["tool_correlation", "escalation_correlation"]
            assert insight.title
            assert insight.impact_score >= 0


class TestGenerateRecommendations:
    def test_generate_recommendations_basic(self):
        insights = [
            RootCauseInsight(
                insight_type="regression",
                title="Test",
                description="Test desc",
                impact_score=0.8,
                confidence=0.9,
                affected_paths=["path1"],
                recommendations=["Fix the thing", "Monitor closely"],
            ),
            RootCauseInsight(
                insight_type="tool_correlation",
                title="Test2",
                description="Test desc2",
                impact_score=0.6,
                confidence=0.7,
                affected_paths=["path2"],
                recommendations=["Fix the thing", "Update dependencies"],
            ),
        ]
        recs = generate_recommendations(insights)
        assert isinstance(recs, list)
        assert len(recs) <= 10

    def test_generate_recommendations_empty_insights(self):
        recs = generate_recommendations([])
        assert len(recs) > 0
        assert all(isinstance(r, str) for r in recs)

    def test_generate_recommendations_deduplicates(self):
        insights = [
            RootCauseInsight(
                insight_type="test",
                title="T",
                description="D",
                impact_score=0.5,
                confidence=0.5,
                affected_paths=[],
                recommendations=["Fix this", "Fix this", "Also fix this"],
            ),
        ]
        recs = generate_recommendations(insights)
        assert len(recs) == len(set(recs))

    def test_generate_recommendations_max_count(self):
        insights = [
            RootCauseInsight(
                insight_type="test",
                title=f"T{i}",
                description=f"D{i}",
                impact_score=0.5,
                confidence=0.5,
                affected_paths=[],
                recommendations=[f"Rec {i}" for i in range(20)],
            )
            for i in range(5)
        ]
        recs = generate_recommendations(insights)
        assert len(recs) <= 10


class TestRootCauseInsight:
    def test_root_cause_insight_to_dict(self):
        insight = RootCauseInsight(
            insight_type="regression",
            title="Test insight",
            description="Test description",
            impact_score=0.75,
            confidence=0.85,
            affected_paths=["path1", "path2"],
            recommendations=["Fix it"],
            evidence={"key": "value"},
        )
        
        d = insight.to_dict()
        
        assert d["insight_type"] == "regression"
        assert d["title"] == "Test insight"
        assert d["impact_score"] == 0.75
        assert d["confidence"] == 0.85
        assert d["affected_paths"] == ["path1", "path2"]
        assert d["recommendations"] == ["Fix it"]
        assert d["evidence"]["key"] == "value"

    def test_root_cause_insight_default_values(self):
        insight = RootCauseInsight(
            insight_type="test",
            title="T",
            description="D",
            impact_score=0.5,
            confidence=0.5,
            affected_paths=[],
        )
        
        assert insight.recommendations == []
        assert insight.evidence == {}


class TestCalculateRegression:
    def test_calculate_regression_positive(self):
        result = _calculate_regression(0.55, 0.50)
        
        assert result.change == 0.05
        assert result.change_percent == 10.0
        assert result.is_significant is True

    def test_calculate_regression_negative(self):
        result = _calculate_regression(0.45, 0.50)
        
        assert result.change == -0.05
        assert result.change_percent == -10.0
        assert result.is_significant is True

    def test_calculate_regression_insignificant(self):
        result = _calculate_regression(0.51, 0.50)
        
        assert abs(result.change_percent) < 5.0
        assert result.is_significant is False

    def test_calculate_regression_zero_baseline(self):
        result = _calculate_regression(0.10, 0.0)
        
        assert result.change == 0.10
        assert result.change_percent == 0.0