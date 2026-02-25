import pytest
from app.version_intelligence import VersionIntelligence


@pytest.fixture
def vi():
    return VersionIntelligence()


@pytest.fixture
def sample_versions():
    return [
        {"version_id": "v1.0", "parent": None, "success_rate": 0.75, "csat": 3.5, "latency": 200},
        {"version_id": "v1.1", "parent": "v1.0", "success_rate": 0.78, "csat": 3.7, "latency": 190},
        {"version_id": "v2.0", "parent": "v1.1", "success_rate": 0.82, "csat": 4.0, "latency": 170},
        {"version_id": "v1.2", "parent": "v1.0", "success_rate": 0.76, "csat": 3.6, "latency": 195},
    ]


class TestBuildLineage:
    def test_build_lineage_basic(self, vi, sample_versions):
        lineage = vi.build_lineage(sample_versions)

        assert "root" in lineage
        assert "nodes" in lineage
        assert "edges" in lineage
        assert "depth" in lineage

    def test_build_lineage_root(self, vi, sample_versions):
        lineage = vi.build_lineage(sample_versions)

        assert lineage["root"] == "v1.0"

    def test_build_lineage_edges(self, vi, sample_versions):
        lineage = vi.build_lineage(sample_versions)

        assert len(lineage["edges"]) == 3

    def test_build_lineage_children(self, vi, sample_versions):
        lineage = vi.build_lineage(sample_versions)

        assert "v1.1" in lineage["nodes"]["v1.0"]["children"]
        assert "v1.2" in lineage["nodes"]["v1.0"]["children"]
        assert "v2.0" in lineage["nodes"]["v1.1"]["children"]

    def test_build_lineage_depths(self, vi, sample_versions):
        lineage = vi.build_lineage(sample_versions)

        assert lineage["depth"]["v1.0"] == 0
        assert lineage["depth"]["v1.1"] == 1
        assert lineage["depth"]["v2.0"] == 2

    def test_build_lineage_empty(self, vi):
        lineage = vi.build_lineage([])

        assert lineage["root"] is None
        assert lineage["nodes"] == {}
        assert lineage["edges"] == []


class TestDiffVersions:
    def test_diff_versions_basic(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75, "csat": 3.5}
        to_v = {"version_id": "v1.1", "success_rate": 0.82, "csat": 4.0}
        diff = vi.diff_versions(from_v, to_v)

        assert diff["from_version"] == "v1.0"
        assert diff["to_version"] == "v1.1"
        assert "deltas" in diff

    def test_diff_versions_deltas(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75, "csat": 3.5}
        to_v = {"version_id": "v1.1", "success_rate": 0.82, "csat": 4.0}
        diff = vi.diff_versions(from_v, to_v)

        assert diff["deltas"]["success_rate"]["from"] == 0.75
        assert diff["deltas"]["success_rate"]["to"] == 0.82
        assert diff["deltas"]["success_rate"]["abs_diff"] == pytest.approx(0.07, rel=0.01)

    def test_diff_versions_regressions(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.82, "latency": 200}
        to_v = {"version_id": "v1.1", "success_rate": 0.75, "latency": 170}
        diff = vi.diff_versions(from_v, to_v)

        assert "latency" in diff["regressions"]
        assert diff["deltas"]["latency"]["direction"] == "regressed"

    def test_diff_versions_improvements(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75}
        to_v = {"version_id": "v1.1", "success_rate": 0.82}
        diff = vi.diff_versions(from_v, to_v)

        assert "success_rate" in diff["improvements"]

    def test_diff_versions_new_metrics(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75}
        to_v = {"version_id": "v1.1", "success_rate": 0.82, "csat": 4.0}
        diff = vi.diff_versions(from_v, to_v)

        assert "csat" in diff["new_metrics"]

    def test_diff_versions_removed_metrics(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75, "old_metric": 1.0}
        to_v = {"version_id": "v1.1", "success_rate": 0.82}
        diff = vi.diff_versions(from_v, to_v)

        assert "old_metric" in diff["removed_metrics"]

    def test_diff_versions_identical(self, vi):
        from_v = {"version_id": "v1.0", "success_rate": 0.75}
        to_v = {"version_id": "v1.1", "success_rate": 0.75}
        diff = vi.diff_versions(from_v, to_v)

        assert diff["deltas"]["success_rate"]["direction"] == "unchanged"


class TestAnalyzeTrend:
    def test_analyze_trend_improving(self, vi):
        versions = [
            {"sequence": 1, "success_rate": 0.70},
            {"sequence": 2, "success_rate": 0.75},
            {"sequence": 3, "success_rate": 0.80},
            {"sequence": 4, "success_rate": 0.85},
        ]
        trend = vi.analyze_trend(versions)

        assert trend["direction"] == "improving"
        assert "trends" in trend
        assert trend["version_count"] == 4

    def test_analyze_trend_degrading(self, vi):
        versions = [
            {"sequence": 1, "success_rate": 0.85},
            {"sequence": 2, "success_rate": 0.80},
            {"sequence": 3, "success_rate": 0.75},
        ]
        trend = vi.analyze_trend(versions)

        assert trend["trends"]["success_rate"]["direction"] == "degrading"

    def test_analyze_trend_insufficient_data(self, vi):
        versions = [{"sequence": 1, "success_rate": 0.75}]
        trend = vi.analyze_trend(versions)

        assert trend["direction"] == "insufficient_data"

    def test_analyze_trend_empty(self, vi):
        trend = vi.analyze_trend([])

        assert trend["direction"] == "insufficient_data"

    def test_analyze_trend_multiple_metrics(self, vi):
        versions = [
            {"sequence": 1, "success_rate": 0.70, "csat": 3.5},
            {"sequence": 2, "success_rate": 0.75, "csat": 3.7},
            {"sequence": 3, "success_rate": 0.80, "csat": 3.9},
        ]
        trend = vi.analyze_trend(versions)

        assert "success_rate" in trend["trends"]
        assert "csat" in trend["trends"]


class TestDetectRegressions:
    def test_detect_regressions_basic(self, vi):
        versions = [
            {"version_id": "v1", "success_rate": 0.85},
            {"version_id": "v2", "success_rate": 0.83},
            {"version_id": "v3", "success_rate": 0.80},
            {"version_id": "v4", "success_rate": 0.70},
            {"version_id": "v5", "success_rate": 0.82},
        ]
        regressions = vi.detect_regressions(versions, "success_rate", window=3)

        assert len(regressions) > 0
        assert regressions[0]["metric"] == "success_rate"

    def test_detect_regressions_severity(self, vi):
        versions = [
            {"version_id": "v1", "success_rate": 0.90},
            {"version_id": "v2", "success_rate": 0.88},
            {"version_id": "v3", "success_rate": 0.85},
            {"version_id": "v4", "success_rate": 0.40},
        ]
        regressions = vi.detect_regressions(versions, "success_rate", window=3)

        assert len(regressions) > 0
        assert regressions[0]["severity"] in ("critical", "major", "minor")

    def test_detect_regressions_no_regression(self, vi):
        versions = [
            {"version_id": "v1", "success_rate": 0.80},
            {"version_id": "v2", "success_rate": 0.82},
            {"version_id": "v3", "success_rate": 0.85},
        ]
        regressions = vi.detect_regressions(versions, "success_rate")

        assert len(regressions) == 0

    def test_detect_regressions_insufficient_versions(self, vi):
        versions = [{"version_id": "v1", "success_rate": 0.80}]
        regressions = vi.detect_regressions(versions, "success_rate")

        assert regressions == []

    def test_detect_regressions_empty(self, vi):
        regressions = vi.detect_regressions([], "success_rate")

        assert regressions == []

    def test_detect_regressions_missing_metric(self, vi):
        versions = [
            {"version_id": "v1", "success_rate": 0.85},
            {"version_id": "v2", "other_metric": 10},
        ]
        regressions = vi.detect_regressions(versions, "missing_metric")

        assert len(regressions) == 0


class TestGetVersionTree:
    def test_get_version_tree_basic(self, vi, sample_versions):
        tree = vi.get_version_tree(sample_versions)

        assert len(tree) > 0
        assert tree[0]["version_id"] == "v1.0"

    def test_get_version_tree_nested(self, vi, sample_versions):
        tree = vi.get_version_tree(sample_versions)

        v1_children = tree[0].get("children", [])
        assert len(v1_children) == 2

    def test_get_version_tree_depth(self, vi, sample_versions):
        tree = vi.get_version_tree(sample_versions)

        assert tree[0]["depth"] == 0
        assert tree[0]["children"][0]["depth"] == 1

    def test_get_version_tree_empty(self, vi):
        tree = vi.get_version_tree([])

        assert tree == []

# history: test: add version intelligence unit tests