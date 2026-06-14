from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


@dataclass
class RootCauseInsight:
    insight_type: str
    title: str
    description: str
    impact_score: float
    confidence: float
    affected_paths: List[str]
    recommendations: List[str] = field(default_factory=list)
    evidence: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insight_type": self.insight_type,
            "title": self.title,
            "description": self.description,
            "impact_score": round(self.impact_score, 4),
            "confidence": round(self.confidence, 4),
            "affected_paths": self.affected_paths,
            "recommendations": self.recommendations,
            "evidence": self.evidence,
        }


@dataclass
class RegressionResult:
    current_value: float
    baseline_value: float
    change: float
    change_percent: float
    is_significant: bool


def _calculate_regression(current: float, baseline: float) -> RegressionResult:
    change = current - baseline
    change_percent = (change / baseline * 100) if baseline != 0 else 0.0
    is_significant = abs(change_percent) > 5.0
    return RegressionResult(
        current_value=current,
        baseline_value=baseline,
        change=change,
        change_percent=change_percent,
        is_significant=is_significant,
    )


def detect_regressions(
    current_sessions: List[Any], baseline_sessions: List[Any]
) -> List[RootCauseInsight]:
    if not current_sessions or not baseline_sessions:
        return []
    
    insights = []
    
    current_by_version = _group_by_version(current_sessions)
    baseline_by_version = _group_by_version(baseline_sessions)
    
    for version in current_by_version:
        if version not in baseline_by_version:
            continue
        
        current_data = current_by_version[version]
        baseline_data = baseline_by_version[version]
        
        current_resolution = current_data["resolved"] / max(current_data["total"], 1)
        baseline_resolution = baseline_data["resolved"] / max(baseline_data["total"], 1)
        resolution_reg = _calculate_regression(current_resolution, baseline_resolution)
        
        if resolution_reg.is_significant and resolution_reg.change < 0:
            current_csat = statistics.mean(current_data["csats"]) if current_data["csats"] else 0
            baseline_csat = statistics.mean(baseline_data["csats"]) if baseline_data["csats"] else 0
            csat_reg = _calculate_regression(current_csat, baseline_csat)
            
            impact = abs(resolution_reg.change_percent) / 100 * current_data["total"]
            
            insight = RootCauseInsight(
                insight_type="regression",
                title=f"Resolution rate dropped for {version}",
                description=(
                    f"Agent version {version} shows a {abs(resolution_reg.change_percent):.1f}% "
                    f"decrease in resolution rate compared to baseline. "
                    f"Current: {current_resolution:.1%}, Baseline: {baseline_resolution:.1%}"
                ),
                impact_score=min(impact / 1000, 1.0),
                confidence=0.85 if csat_reg.is_significant else 0.6,
                affected_paths=_find_affected_paths(current_sessions, version),
                recommendations=[
                    f"Review changes made in {version} release",
                    f"Compare prompt versions between baseline and current",
                    "Check for tool availability issues",
                    "Analyze if specific workflows are affected",
                ],
                evidence={
                    "current_resolution": round(current_resolution, 4),
                    "baseline_resolution": round(baseline_resolution, 4),
                    "change_percent": round(resolution_reg.change_percent, 2),
                    "current_csat": round(current_csat, 2),
                    "baseline_csat": round(baseline_csat, 2),
                    "session_count": current_data["total"],
                },
            )
            insights.append(insight)
    
    path_current = _group_by_path(current_sessions)
    path_baseline = _group_by_path(baseline_sessions)
    
    for path_id in path_current:
        if path_id not in path_baseline:
            continue
        
        current_data = path_current[path_id]
        baseline_data = path_baseline[path_id]
        
        if baseline_data["total"] < 20:
            continue
        
        current_rate = current_data["resolved"] / max(current_data["total"], 1)
        baseline_rate = baseline_data["resolved"] / max(baseline_data["total"], 1)
        rate_reg = _calculate_regression(current_rate, baseline_rate)
        
        if rate_reg.is_significant and rate_reg.change < 0:
            current_latency = statistics.mean(current_data["latencies"]) if current_data["latencies"] else 0
            baseline_latency = statistics.mean(baseline_data["latencies"]) if baseline_data["latencies"] else 0
            latency_reg = _calculate_regression(current_latency, baseline_latency)
            
            impact = abs(rate_reg.change_percent) * current_data["total"] / 100
            
            insight = RootCauseInsight(
                insight_type="path_regression",
                title=f"Path '{path_id}' success rate declined",
                description=(
                    f"Workflow path {path_id} experienced a {abs(rate_reg.change_percent):.1f}% "
                    f"drop in resolution rate. Current: {current_rate:.1%}, Baseline: {baseline_rate:.1%}"
                ),
                impact_score=min(impact / 500, 1.0),
                confidence=0.8,
                affected_paths=[path_id],
                recommendations=[
                    f"Analyze steps in {path_id} for bottlenecks",
                    "Check if CRM or KB lookup times increased",
                    "Review error logs for this workflow",
                    "Consider adding monitoring for path-specific metrics",
                ],
                evidence={
                    "current_rate": round(current_rate, 4),
                    "baseline_rate": round(baseline_rate, 4),
                    "change_percent": round(rate_reg.change_percent, 2),
                    "current_latency_ms": round(current_latency, 2),
                    "baseline_latency_ms": round(baseline_latency, 2),
                    "path_session_count": current_data["total"],
                },
            )
            insights.append(insight)
    
    insights.sort(key=lambda x: x.impact_score, reverse=True)
    return insights


def find_correlated_failures(
    traces: List[Any], outcomes: Optional[List[str]] = None
) -> List[RootCauseInsight]:
    if not traces:
        return []
    
    tool_impact = _analyze_tool_impact(traces)
    
    insights = []
    
    for tool_name, impact in tool_impact.items():
        if impact["failure_count"] < 50:
            continue
        
        if impact["csat_drop"] > 0.3:
            confidence = min(0.5 + impact["failure_count"] / 1000, 0.95)
            
            insight = RootCauseInsight(
                insight_type="tool_correlation",
                title=f"Tool '{tool_name}' failures correlate with lower satisfaction",
                description=(
                    f"Sessions with {tool_name} failures show a {impact['csat_drop']:.2f} "
                    f"point lower CSAT on average. Failure count: {impact['failure_count']}"
                ),
                impact_score=min(impact["csat_drop"] * impact["failure_count"] / 500, 1.0),
                confidence=confidence,
                affected_paths=impact.get("affected_paths", []),
                recommendations=[
                    f"Improve reliability of {tool_name}",
                    "Add retry logic for failed calls",
                    "Check external service dependencies",
                    "Consider fallback mechanisms",
                ],
                evidence={
                    "csat_with_failure": round(impact["csat_with"], 2),
                    "csat_without_failure": round(impact["csat_without"], 2),
                    "csat_drop": round(impact["csat_drop"], 2),
                    "failure_count": impact["failure_count"],
                    "escalation_increase": round(impact.get("escalation_increase", 0), 4),
                },
            )
            insights.append(insight)
        
        if impact.get("escalation_increase", 0) > 0.1:
            confidence = min(0.6 + impact["failure_count"] / 2000, 0.95)
            
            insight = RootCauseInsight(
                insight_type="escalation_correlation",
                title=f"'{tool_name}' failures lead to escalations",
                description=(
                    f"Sessions with {tool_name} failures have a {impact['escalation_increase']:.1%} "
                    f"higher escalation rate. Escalation impact: {impact.get('escalation_diff', 0)}"
                ),
                impact_score=min(impact["escalation_increase"] * 5, 1.0),
                confidence=confidence,
                affected_paths=impact.get("affected_paths", []),
                recommendations=[
                    f"Analyze {tool_name} failure patterns",
                    "Implement circuit breaker pattern",
                    "Add alerting for failure thresholds",
                    "Review data quality for {tool_name} dependencies",
                ],
                evidence={
                    "escalation_with_failure": round(impact.get("escalation_with", 0), 4),
                    "escalation_without_failure": round(impact.get("escalation_without", 0), 4),
                    "escalation_increase": round(impact["escalation_increase"], 4),
                    "failure_count": impact["failure_count"],
                },
            )
            insights.append(insight)
    
    insights.sort(key=lambda x: x.impact_score, reverse=True)
    return insights


def generate_recommendations(insights: List[RootCauseInsight]) -> List[str]:
    if not insights:
        return [
            "Continue monitoring current metrics",
            "Establish baseline metrics if not already done",
            "Set up alerts for significant metric changes",
        ]
    
    recommendations = []
    seen = set()
    
    for insight in insights:
        for rec in insight.recommendations:
            rec_lower = rec.lower()
            if rec_lower not in seen:
                seen.add(rec_lower)
                recommendations.append(rec)
    
    if not recommendations:
        recommendations = [
            "No specific recommendations - metrics within normal range",
            "Continue regular monitoring",
        ]
    
    return recommendations[:10]


def _group_by_version(sessions: List[Any]) -> Dict[str, Dict]:
    groups = defaultdict(lambda: {
        "total": 0,
        "resolved": 0,
        "escalated": 0,
        "csats": [],
        "latencies": [],
    })
    
    for session in sessions:
        version = getattr(session, "agent_version", None)
        if not version:
            continue
        
        data = groups[version]
        data["total"] += 1
        
        outcome = getattr(session, "outcome", "unknown")
        if outcome == "resolved":
            data["resolved"] += 1
        elif outcome == "escalated":
            data["escalated"] += 1
        
        csat = getattr(session, "csat_score", 0)
        if csat:
            data["csats"].append(csat)
        
        latency = getattr(session, "latency_ms", 0)
        if latency:
            data["latencies"].append(latency)
    
    return groups


def _group_by_path(sessions: List[Any]) -> Dict[str, Dict]:
    groups = defaultdict(lambda: {
        "total": 0,
        "resolved": 0,
        "latencies": [],
        "versions": set(),
    })
    
    for session in sessions:
        path_id = getattr(session, "path_id", None)
        if not path_id:
            continue
        
        data = groups[path_id]
        data["total"] += 1
        
        outcome = getattr(session, "outcome", "unknown")
        if outcome == "resolved":
            data["resolved"] += 1
        
        latency = getattr(session, "latency_ms", 0)
        if latency:
            data["latencies"].append(latency)
        
        version = getattr(session, "agent_version", None)
        if version:
            data["versions"].add(version)
    
    return groups


def _find_affected_paths(sessions: List[Any], version: str) -> List[str]:
    paths = set()
    for session in sessions:
        if getattr(session, "agent_version", None) == version:
            path_id = getattr(session, "path_id", None)
            if path_id:
                paths.add(path_id)
    return list(paths)[:5]


def _analyze_tool_impact(traces: List[Any]) -> Dict[str, Dict]:
    tool_data = defaultdict(lambda: {
        "with_failure": {"csats": [], "escalated": 0, "total": 0, "paths": set()},
        "without_failure": {"csats": [], "escalated": 0, "total": 0, "paths": set()},
    })
    
    all_tools = ["search", "crm_lookup", "kb_search", "escalate", "respond", "transfer"]
    
    for trace in traces:
        tool_failures = getattr(trace, "tool_failures", [])
        if isinstance(tool_failures, str):
            tool_failures = [f.strip().replace("_retry", "") for f in tool_failures.split(",") if f.strip()]
        else:
            tool_failures = [f.strip().replace("_retry", "") for f in tool_failures if f.strip()]
        
        csat = getattr(trace, "csat_score", 0)
        outcome = getattr(trace, "outcome", "unknown")
        path_id = getattr(trace, "path_id", "unknown")
        
        for tool in all_tools:
            had_failure = tool in tool_failures
            
            if had_failure:
                data = tool_data[tool]["with_failure"]
            else:
                data = tool_data[tool]["without_failure"]
            
            data["total"] += 1
            if csat:
                data["csats"].append(csat)
            if outcome == "escalated":
                data["escalated"] += 1
            data["paths"].add(path_id)
    
    impacts = {}
    for tool, data in tool_data.items():
        wf = data["with_failure"]
        wof = data["without_failure"]
        
        if wf["total"] < 20 or wof["total"] < 20:
            continue
        
        csat_with = statistics.mean(wf["csats"]) if wf["csats"] else 0
        csat_without = statistics.mean(wof["csats"]) if wof["csats"] else 0
        
        escalation_with = wf["escalated"] / max(wf["total"], 1)
        escalation_without = wof["escalated"] / max(wof["total"], 1)
        
        impacts[tool] = {
            "failure_count": wf["total"],
            "csat_with": csat_with,
            "csat_without": csat_without,
            "csat_drop": csat_without - csat_with,
            "escalation_with": escalation_with,
            "escalation_without": escalation_without,
            "escalation_increase": escalation_with - escalation_without,
            "escalation_diff": escalation_with - escalation_without,
            "affected_paths": list(wf["paths"])[:5],
        }
    
    return impacts