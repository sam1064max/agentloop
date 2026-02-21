from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import defaultdict


@dataclass
class PathAnalysisResult:
    path_id: str
    steps: List[str]
    success_rate: float
    count: int
    avg_latency_ms: float
    avg_cost: float
    avg_csat: float
    outcome_distribution: Dict[str, int] = None
    
    def __post_init__(self):
        if self.outcome_distribution is None:
            self.outcome_distribution = {}


def analyze_paths(sessions: List[Any]) -> List[PathAnalysisResult]:
    if not sessions:
        return []
    
    path_data = defaultdict(lambda: {
        "steps": None,
        "total": 0,
        "resolved": 0,
        "escalated": 0,
        "converted": 0,
        "retained": 0,
        "latencies": [],
        "costs": [],
        "csats": [],
    })
    
    for session in sessions:
        path_id = getattr(session, "path_id", None)
        if not path_id:
            continue
        
        data = path_data[path_id]
        data["total"] += 1
        
        if data["steps"] is None:
            data["steps"] = getattr(session, "steps", [])
        
        outcome = getattr(session, "outcome", "unknown")
        if outcome == "resolved":
            data["resolved"] += 1
        elif outcome == "escalated":
            data["escalated"] += 1
        elif outcome == "converted":
            data["converted"] += 1
        elif outcome == "retained":
            data["retained"] += 1
        
        latencies = getattr(session, "latency_ms", 0)
        if latencies:
            data["latencies"].append(latencies)
        
        costs = getattr(session, "cost", 0)
        if costs:
            data["costs"].append(costs)
        
        csats = getattr(session, "csat_score", 0)
        if csats:
            data["csats"].append(csats)
    
    results = []
    for path_id, data in path_data.items():
        if data["total"] == 0:
            continue
        
        success_rate = data["resolved"] / data["total"]
        
        avg_latency = (
            sum(data["latencies"]) / len(data["latencies"])
            if data["latencies"]
            else 0.0
        )
        
        avg_cost = sum(data["costs"]) / len(data["costs"]) if data["costs"] else 0.0
        
        avg_csat = sum(data["csats"]) / len(data["csats"]) if data["csats"] else 0.0
        
        outcome_distribution = {
            "resolved": data["resolved"],
            "escalated": data["escalated"],
            "converted": data["converted"],
            "retained": data["retained"],
        }
        
        result = PathAnalysisResult(
            path_id=path_id,
            steps=data["steps"],
            success_rate=round(success_rate, 4),
            count=data["total"],
            avg_latency_ms=round(avg_latency, 2),
            avg_cost=round(avg_cost, 6),
            avg_csat=round(avg_csat, 2),
            outcome_distribution=outcome_distribution,
        )
        results.append(result)
    
    results.sort(key=lambda x: x.count, reverse=True)
    return results


def rank_paths_by_outcome(
    paths: List[PathAnalysisResult], outcome: str
) -> List[PathAnalysisResult]:
    if not paths:
        return []
    
    if outcome == "success_rate":
        return sorted(paths, key=lambda x: x.success_rate, reverse=True)
    elif outcome == "resolution":
        def resolution_weight(p):
            return p.outcome_distribution.get("resolved", 0) / max(p.count, 1)
        return sorted(paths, key=resolution_weight, reverse=True)
    elif outcome == "csat":
        return sorted(paths, key=lambda x: x.avg_csat, reverse=True)
    elif outcome == "latency":
        return sorted(paths, key=lambda x: x.avg_latency_ms)
    elif outcome == "volume":
        return sorted(paths, key=lambda x: x.count, reverse=True)
    elif outcome in ["escalated", "converted", "retained"]:
        def outcome_weight(p):
            return p.outcome_distribution.get(outcome, 0) / max(p.count, 1)
        return sorted(paths, key=outcome_weight, reverse=True)
    else:
        return paths


def find_top_paths(paths: List[PathAnalysisResult], limit: int = 5) -> List[PathAnalysisResult]:
    return sorted(paths, key=lambda x: x.count, reverse=True)[:limit]


def find_best_performing_paths(
    paths: List[PathAnalysisResult], min_count: int = 100
) -> List[PathAnalysisResult]:
    filtered = [p for p in paths if p.count >= min_count]
    return sorted(filtered, key=lambda x: x.success_rate, reverse=True)


def find_worst_performing_paths(
    paths: List[PathAnalysisResult], min_count: int = 100
) -> List[PathAnalysisResult]:
    filtered = [p for p in paths if p.count >= min_count]
    return sorted(filtered, key=lambda x: x.success_rate)[:min_count]


def compare_paths(path1_id: str, path2_id: str, paths: List[PathAnalysisResult]) -> Dict[str, Any]:
    p1 = next((p for p in paths if p.path_id == path1_id), None)
    p2 = next((p for p in paths if p.path_id == path2_id), None)
    
    if not p1 or not p2:
        return {}
    
    return {
        "path1": path1_id,
        "path2": path2_id,
        "success_rate_diff": round(p1.success_rate - p2.success_rate, 4),
        "latency_diff": round(p1.avg_latency_ms - p2.avg_latency_ms, 2),
        "cost_diff": round(p1.avg_cost - p2.avg_cost, 6),
        "csat_diff": round(p1.avg_csat - p2.avg_csat, 2),
        "count_diff": p1.count - p2.count,
    }
# history: feat: add path analyzer for version-specific workflows