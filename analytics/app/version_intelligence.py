from typing import List, Dict, Any, Optional
import numpy as np
from scipy import stats as scipy_stats
from collections import defaultdict


class VersionIntelligence:
    def build_lineage(self, versions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not versions:
            return {"root": None, "nodes": {}, "edges": []}

        version_map = {}
        for v in versions:
            vid = v.get("version_id", v.get("id", ""))
            parent = v.get("parent_version", v.get("parent", None))
            version_map[vid] = {
                "version_id": vid,
                "parent": parent,
                "children": [],
                "metadata": {k: v for k, v in v.items() if k not in ("version_id", "parent_version", "parent", "id")},
            }

        for vid, node in version_map.items():
            parent = node["parent"]
            if parent and parent in version_map:
                version_map[parent]["children"].append(vid)

        roots = [vid for vid, node in version_map.items() if node["parent"] is None or node["parent"] not in version_map]

        edges = []
        for vid, node in version_map.items():
            if node["parent"] and node["parent"] in version_map:
                edges.append({"from": node["parent"], "to": vid})

        return {
            "root": roots[0] if roots else None,
            "nodes": version_map,
            "edges": edges,
            "depth": self._calculate_depth(version_map, roots),
        }

    def _calculate_depth(
        self, nodes: Dict[str, Any], roots: List[str]
    ) -> Dict[str, int]:
        depth = {}
        def dfs(vid: str, d: int):
            depth[vid] = d
            for child in nodes[vid]["children"]:
                dfs(child, d + 1)

        for root in roots:
            if root in nodes:
                dfs(root, 0)
        return depth

    def diff_versions(
        self, from_v: Dict[str, Any], to_v: Dict[str, Any]
    ) -> Dict[str, Any]:
        metrics_from = {k: v for k, v in from_v.items() if isinstance(v, (int, float)) and k not in ("id", "version_id")}
        metrics_to = {k: v for k, v in to_v.items() if isinstance(v, (int, float)) and k not in ("id", "version_id")}

        all_metrics = set(metrics_from.keys()) | set(metrics_to.keys())
        deltas = {}
        for metric in sorted(all_metrics):
            val_from = metrics_from.get(metric, 0)
            val_to = metrics_to.get(metric, 0)
            abs_diff = val_to - val_from
            pct_change = (
                (abs_diff / abs(val_from)) * 100 if val_from != 0
                else (float("inf") if val_to != 0 else 0.0)
            )
            deltas[metric] = {
                "from": val_from,
                "to": val_to,
                "abs_diff": round(abs_diff, 4),
                "pct_change": round(pct_change, 2),
                "direction": "improved" if abs_diff > 0 else ("regressed" if abs_diff < 0 else "unchanged"),
            }

        new_metrics = [m for m in sorted(all_metrics) if m not in metrics_from]
        removed_metrics = [m for m in sorted(all_metrics) if m not in metrics_to]

        return {
            "from_version": from_v.get("version_id", from_v.get("id", "unknown")),
            "to_version": to_v.get("version_id", to_v.get("id", "unknown")),
            "deltas": deltas,
            "new_metrics": new_metrics,
            "removed_metrics": removed_metrics,
            "regressions": [
                m for m, d in deltas.items() if d["direction"] == "regressed"
            ],
            "improvements": [
                m for m, d in deltas.items() if d["direction"] == "improved"
            ],
        }

    def analyze_trend(
        self, version_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not version_metrics or len(version_metrics) < 2:
            return {
                "direction": "insufficient_data",
                "slope": 0.0,
                "p_value": 1.0,
                "significant": False,
            }

        sorted_versions = sorted(
            version_metrics,
            key=lambda v: v.get("sequence", v.get("version", ""))
        )

        metric_keys = set()
        for v in sorted_versions:
            for k, val in v.items():
                if isinstance(val, (int, float)) and k not in ("sequence",):
                    metric_keys.add(k)

        trends = {}
        for metric in sorted(metric_keys):
            x_vals = []
            y_vals = []
            for i, v in enumerate(sorted_versions):
                mval = v.get(metric)
                if mval is not None and isinstance(mval, (int, float)):
                    x_vals.append(float(i))
                    y_vals.append(float(mval))

            if len(x_vals) < 2:
                trends[metric] = {"slope": 0.0, "p_value": 1.0, "significant": False}
                continue

            x = np.array(x_vals)
            y = np.array(y_vals)
            slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(x, y)

            trends[metric] = {
                "slope": round(float(slope), 4),
                "intercept": round(float(intercept), 4),
                "r_squared": round(float(r_value ** 2), 4),
                "p_value": round(float(p_value), 6),
                "significant": p_value < 0.05,
                "direction": "improving" if slope > 0 else ("degrading" if slope < 0 else "stable"),
            }

        improving = sum(1 for t in trends.values() if t["direction"] == "improving" and t["significant"])
        degrading = sum(1 for t in trends.values() if t["direction"] == "degrading" and t["significant"])

        if improving > degrading:
            overall = "improving"
        elif degrading > improving:
            overall = "degrading"
        else:
            overall = "mixed"

        return {
            "direction": overall,
            "version_count": len(sorted_versions),
            "improving_metrics": improving,
            "degrading_metrics": degrading,
            "trends": trends,
        }

    def detect_regressions(
        self, versions: List[Dict[str, Any]], metric: str, window: int = 7
    ) -> List[Dict[str, Any]]:
        if not versions or len(versions) < 2:
            return []

        sorted_versions = sorted(
            versions,
            key=lambda v: v.get("sequence", v.get("version", ""))
        )

        regressions = []
        for i in range(1, len(sorted_versions)):
            current = sorted_versions[i]
            previous = sorted_versions[i - 1]

            cur_val = current.get(metric)
            prev_val = previous.get(metric)

            if cur_val is None or prev_val is None:
                continue

            if not isinstance(cur_val, (int, float)) or not isinstance(prev_val, (int, float)):
                continue

            if cur_val < prev_val:
                window_start = max(0, i - window)
                window_vals = [
                    sorted_versions[j].get(metric)
                    for j in range(window_start, i)
                    if sorted_versions[j].get(metric) is not None
                ]
                window_vals = [float(v) for v in window_vals if isinstance(v, (int, float))]

                window_mean = np.mean(window_vals) if window_vals else prev_val
                window_std = np.std(window_vals, ddof=1) if len(window_vals) > 1 else 1.0

                z_score = (cur_val - window_mean) / window_std if window_std > 0 else 0.0
                pct_drop = ((cur_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0.0

                severity = "critical" if z_score < -3 else ("major" if z_score < -2 else "minor")

                regressions.append({
                    "version": current.get("version_id", current.get("id", f"v{i}")),
                    "metric": metric,
                    "previous_value": float(prev_val),
                    "current_value": float(cur_val),
                    "abs_drop": round(float(prev_val - cur_val), 4),
                    "pct_drop": round(float(pct_drop), 2),
                    "z_score": round(float(z_score), 4),
                    "severity": severity,
                    "window_mean": round(float(window_mean), 4),
                    "window_size": len(window_vals),
                })

        regressions.sort(key=lambda r: r["z_score"])
        return regressions

    def get_version_tree(
        self, versions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        lineage = self.build_lineage(versions)
        roots = [
            vid for vid, node in lineage["nodes"].items()
            if node["parent"] is None or node["parent"] not in lineage["nodes"]
        ]

        tree = []
        def build_subtree(vid: str, depth: int = 0):
            node = lineage["nodes"].get(vid)
            if not node:
                return None

            entry = {
                "version_id": vid,
                "depth": depth,
                "children_count": len(node["children"]),
                "metadata": node["metadata"],
            }

            entry["children"] = [
                build_subtree(child, depth + 1)
                for child in node["children"]
            ]
            entry["children"] = [c for c in entry["children"] if c is not None]

            return entry

        for root in roots:
            subtree = build_subtree(root)
            if subtree:
                tree.append(subtree)

        return tree

# history: feat: add VersionIntelligence with lineage builder