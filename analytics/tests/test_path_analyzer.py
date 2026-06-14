import pytest
from collections import namedtuple

from app.path_analyzer import (
    PathAnalysisResult,
    analyze_paths,
    rank_paths_by_outcome,
    find_top_paths,
    find_best_performing_paths,
    find_worst_performing_paths,
    compare_paths,
)

MockSession = namedtuple(
    "MockSession",
    ["session_id", "path_id", "steps", "outcome", "csat_score", "latency_ms", "cost"]
)


@pytest.fixture
def sample_sessions():
    return [
        MockSession(
            session_id="s1",
            path_id="search_crm_kb_respond",
            steps=["search", "crm_lookup", "kb_search", "respond"],
            outcome="resolved",
            csat_score=5,
            latency_ms=220,
            cost=0.008,
        ),
        MockSession(
            session_id="s2",
            path_id="search_crm_kb_respond",
            steps=["search", "crm_lookup", "kb_search", "respond"],
            outcome="resolved",
            csat_score=4,
            latency_ms=230,
            cost=0.009,
        ),
        MockSession(
            session_id="s3",
            path_id="search_crm_kb_respond",
            steps=["search", "crm_lookup", "kb_search", "respond"],
            outcome="escalated",
            csat_score=2,
            latency_ms=250,
            cost=0.010,
        ),
        MockSession(
            session_id="s4",
            path_id="search_kb_respond",
            steps=["search", "kb_search", "respond"],
            outcome="resolved",
            csat_score=5,
            latency_ms=160,
            cost=0.006,
        ),
        MockSession(
            session_id="s5",
            path_id="search_kb_respond",
            steps=["search", "kb_search", "respond"],
            outcome="resolved",
            csat_score=4,
            latency_ms=170,
            cost=0.006,
        ),
        MockSession(
            session_id="s6",
            path_id="search_kb_respond",
            steps=["search", "kb_search", "respond"],
            outcome="resolved",
            csat_score=4,
            latency_ms=155,
            cost=0.005,
        ),
        MockSession(
            session_id="s7",
            path_id="search_escalate",
            steps=["search", "escalate"],
            outcome="escalated",
            csat_score=2,
            latency_ms=120,
            cost=0.004,
        ),
    ]


class TestAnalyzePaths:
    def test_analyze_paths_returns_results(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        assert len(results) > 0
        assert isinstance(results[0], PathAnalysisResult)

    def test_analyze_paths_calculates_success_rate(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        path_results = {r.path_id: r for r in results}
        
        sckr = path_results.get("search_crm_kb_respond")
        assert sckr is not None
        assert sckr.success_rate == pytest.approx(2/3, rel=0.01)
        assert sckr.count == 3

    def test_analyze_paths_calculates_avg_latency(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        path_results = {r.path_id: r for r in results}
        
        skr = path_results.get("search_kb_respond")
        assert skr is not None
        expected_avg = (160 + 170 + 155) / 3
        assert skr.avg_latency_ms == pytest.approx(expected_avg, rel=0.01)

    def test_analyze_paths_outcome_distribution(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        path_results = {r.path_id: r for r in results}
        
        sckr = path_results.get("search_crm_kb_respond")
        assert sckr.outcome_distribution["resolved"] == 2
        assert sckr.outcome_distribution["escalated"] == 1

    def test_analyze_paths_empty_list(self):
        results = analyze_paths([])
        assert results == []

    def test_analyze_paths_missing_attributes(self):
        class PartialSession:
            def __init__(self, sid, outcome):
                self.session_id = sid
                self.outcome = outcome
        
        sessions = [PartialSession("s1", "resolved")]
        results = analyze_paths(sessions)
        assert len(results) == 0


class TestRankPathsByOutcome:
    def test_rank_by_success_rate(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        ranked = rank_paths_by_outcome(results, "success_rate")
        
        assert ranked[0].success_rate >= ranked[1].success_rate

    def test_rank_by_volume(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        ranked = rank_paths_by_outcome(results, "volume")
        
        assert ranked[0].count >= ranked[1].count

    def test_rank_by_latency(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        ranked = rank_paths_by_outcome(results, "latency")
        
        for i in range(len(ranked) - 1):
            assert ranked[i].avg_latency_ms <= ranked[i + 1].avg_latency_ms

    def test_rank_by_csat(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        ranked = rank_paths_by_outcome(results, "csat")
        
        for i in range(len(ranked) - 1):
            assert ranked[i].avg_csat >= ranked[i + 1].avg_csat

    def test_rank_by_escalated(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        ranked = rank_paths_by_outcome(results, "escalated")
        assert len(ranked) > 0

    def test_rank_empty_paths(self):
        ranked = rank_paths_by_outcome([], "volume")
        assert ranked == []


class TestFindPaths:
    def test_find_top_paths(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        top = find_top_paths(results, limit=2)
        
        assert len(top) <= 2
        assert top[0].count >= top[-1].count

    def test_find_best_performing_paths(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        best = find_best_performing_paths(results, min_count=2)
        
        for path in best:
            assert path.count >= 2
            assert path.success_rate >= best[0].success_rate

    def test_find_worst_performing_paths(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        worst = find_worst_performing_paths(results, min_count=1)
        
        if len(worst) > 1:
            assert worst[0].success_rate <= worst[-1].success_rate


class TestComparePaths:
    def test_compare_paths(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        comparison = compare_paths(
            "search_crm_kb_respond",
            "search_kb_respond",
            results
        )
        
        assert comparison["path1"] == "search_crm_kb_respond"
        assert comparison["path2"] == "search_kb_respond"
        assert "success_rate_diff" in comparison
        assert "latency_diff" in comparison

    def test_compare_paths_missing_path(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        comparison = compare_paths("nonexistent", "search_kb_respond", results)
        assert comparison == {}

    def test_compare_paths_both_missing(self, sample_sessions):
        results = analyze_paths(sample_sessions)
        comparison = compare_paths("nonexistent1", "nonexistent2", results)
        assert comparison == {}