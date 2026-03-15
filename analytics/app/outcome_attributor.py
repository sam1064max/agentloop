from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


@dataclass
class OutcomeMetrics:
    total_sessions: int
    resolution_rate: float
    escalation_rate: float
    csat_avg: float
    csat_median: float
    conversion_rate: float
    retention_rate: float
    avg_latency_ms: float
    total_cost: float
    outcome_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_sessions": self.total_sessions,
            "resolution_rate": round(self.resolution_rate, 4),
            "escalation_rate": round(self.escalation_rate, 4),
            "csat_avg": round(self.csat_avg, 2),
            "csat_median": round(self.csat_median, 2),
            "conversion_rate": round(self.conversion_rate, 4),
            "retention_rate": round(self.retention_rate, 4),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "total_cost": round(self.total_cost, 4),
            "outcome_counts": self.outcome_counts,
        }


@dataclass
class AgentVersionMetrics:
    version: str
    total_sessions: int
    resolution_rate: float
    escalation_rate: float
    csat_avg: float
    avg_latency_ms: float
    avg_cost: float
    outcome_distribution: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "total_sessions": self.total_sessions,
            "resolution_rate": round(self.resolution_rate, 4),
            "escalation_rate": round(self.escalation_rate, 4),
            "csat_avg": round(self.csat_avg, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "avg_cost": round(self.avg_cost, 6),
            "outcome_distribution": self.outcome_distribution,
        }


@dataclass
class ToolFailureImpact:
    tool_name: str
    failure_count: int
    failure_rate: float
    avg_latency_impact_ms: float
    csat_impact: float
    escalation_impact: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "failure_count": self.failure_count,
            "failure_rate": round(self.failure_rate, 4),
            "avg_latency_impact_ms": round(self.avg_latency_impact_ms, 2),
            "csat_impact": round(self.csat_impact, 4),
            "escalation_impact": round(self.escalation_impact, 4),
        }


def calculate_outcome_metrics(sessions: List[Any], outcomes: Optional[List[str]] = None) -> OutcomeMetrics:
    if not sessions:
        return OutcomeMetrics(
            total_sessions=0,
            resolution_rate=0.0,
            escalation_rate=0.0,
            csat_avg=0.0,
            csat_median=0.0,
            conversion_rate=0.0,
            retention_rate=0.0,
            avg_latency_ms=0.0,
            total_cost=0.0,
        )
    
    total = len(sessions)
    
    outcome_counts = defaultdict(int)
    csats = []
    latencies = []
    costs = []
    
    for session in sessions:
        outcome = getattr(session, "outcome", "unknown")
        outcome_counts[outcome] += 1
        
        csat = getattr(session, "csat_score", 0)
        if csat:
            csats.append(csat)
        
        latency = getattr(session, "latency_ms", 0)
        if latency:
            latencies.append(latency)
        
        cost = getattr(session, "cost", 0)
        if cost:
            costs.append(cost)
    
    resolution_rate = outcome_counts.get("resolved", 0) / total
    escalation_rate = outcome_counts.get("escalated", 0) / total
    conversion_rate = outcome_counts.get("converted", 0) / total
    retention_rate = outcome_counts.get("retained", 0) / total
    
    csat_avg = statistics.mean(csats) if csats else 0.0
    csat_median = statistics.median(csats) if csats else 0.0
    
    avg_latency = statistics.mean(latencies) if latencies else 0.0
    total_cost = sum(costs)
    
    return OutcomeMetrics(
        total_sessions=total,
        resolution_rate=resolution_rate,
        escalation_rate=escalation_rate,
        csat_avg=csat_avg,
        csat_median=csat_median,
        conversion_rate=conversion_rate,
        retention_rate=retention_rate,
        avg_latency_ms=avg_latency,
        total_cost=total_cost,
        outcome_counts=dict(outcome_counts),
    )


def compare_agent_versions(
    sessions: List[Any], outcomes: Optional[List[str]] = None
) -> Dict[str, AgentVersionMetrics]:
    if not sessions:
        return {}
    
    version_data = defaultdict(lambda: {
        "total": 0,
        "resolved": 0,
        "escalated": 0,
        "converted": 0,
        "retained": 0,
        "csats": [],
        "latencies": [],
        "costs": [],
    })
    
    for session in sessions:
        version = getattr(session, "agent_version", None)
        if not version:
            continue
        
        data = version_data[version]
        data["total"] += 1
        
        outcome = getattr(session, "outcome", "unknown")
        if outcome == "resolved":
            data["resolved"] += 1
        elif outcome == "escalated":
            data["escalated"] += 1
        elif outcome == "converted":
            data["converted"] += 1
        elif outcome == "retained":
            data["retained"] += 1
        
        csat = getattr(session, "csat_score", 0)
        if csat:
            data["csats"].append(csat)
        
        latency = getattr(session, "latency_ms", 0)
        if latency:
            data["latencies"].append(latency)
        
        cost = getattr(session, "cost", 0)
        if cost:
            data["costs"].append(cost)
    
    results = {}
    for version, data in version_data.items():
        if data["total"] == 0:
            continue
        
        resolution_rate = data["resolved"] / data["total"]
        escalation_rate = data["escalated"] / data["total"]
        csat_avg = statistics.mean(data["csats"]) if data["csats"] else 0.0
        avg_latency = statistics.mean(data["latencies"]) if data["latencies"] else 0.0
        avg_cost = statistics.mean(data["costs"]) if data["costs"] else 0.0
        
        metrics = AgentVersionMetrics(
            version=version,
            total_sessions=data["total"],
            resolution_rate=resolution_rate,
            escalation_rate=escalation_rate,
            csat_avg=csat_avg,
            avg_latency_ms=avg_latency,
            avg_cost=avg_cost,
            outcome_distribution={
                "resolved": data["resolved"],
                "escalated": data["escalated"],
                "converted": data["converted"],
                "retained": data["retained"],
            },
        )
        results[version] = metrics
    
    return results


def correlate_tool_failures(
    traces: List[Any], outcomes: Optional[List[str]] = None
) -> List[ToolFailureImpact]:
    if not traces:
        return []
    
    tool_data = defaultdict(lambda: {
        "with_failure": {"total": 0, "csats": [], "escalated": 0, "latencies": []},
        "without_failure": {"total": 0, "csats": [], "escalated": 0, "latencies": []},
    })
    
    for trace in traces:
        tool_failures = getattr(trace, "tool_failures", [])
        if isinstance(tool_failures, str):
            tool_failures = tool_failures.split(",") if tool_failures else []
        tool_failures = [f.strip().replace("_retry", "") for f in tool_failures if f.strip()]
        
        csat = getattr(trace, "csat_score", 0)
        latency = getattr(trace, "latency_ms", 0)
        outcome = getattr(trace, "outcome", "unknown")
        
        all_tools = ["search", "crm_lookup", "kb_search", "escalate", "respond", "transfer"]
        
        for tool in all_tools:
            had_failure = tool in tool_failures
            
            if had_failure:
                data = tool_data[tool]["with_failure"]
            else:
                data = tool_data[tool]["without_failure"]
            
            data["total"] += 1
            if csat:
                data["csats"].append(csat)
            if latency:
                data["latencies"].append(latency)
            if outcome == "escalated":
                data["escalated"] += 1
    
    impacts = []
    for tool, data in tool_data.items():
        wf = data["with_failure"]
        wof = data["without_failure"]
        
        if wf["total"] < 10 or wof["total"] < 10:
            continue
        
        failure_rate = wf["total"] / (wf["total"] + wof["total"])
        
        avg_csat_with = statistics.mean(wf["csats"]) if wf["csats"] else 0.0
        avg_csat_without = statistics.mean(wof["csats"]) if wof["csats"] else 0.0
        csat_impact = avg_csat_with - avg_csat_without
        
        avg_latency_with = statistics.mean(wf["latencies"]) if wf["latencies"] else 0.0
        avg_latency_without = statistics.mean(wof["latencies"]) if wof["latencies"] else 0.0
        latency_impact = avg_latency_with - avg_latency_without
        
        escalation_with = wf["escalated"] / max(wf["total"], 1)
        escalation_without = wof["escalated"] / max(wof["total"], 1)
        escalation_impact = escalation_with - escalation_without
        
        impact = ToolFailureImpact(
            tool_name=tool,
            failure_count=wf["total"],
            failure_rate=failure_rate,
            avg_latency_impact_ms=latency_impact,
            csat_impact=csat_impact,
            escalation_impact=escalation_impact,
        )
        impacts.append(impact)
    
    impacts.sort(key=lambda x: abs(x.csat_impact) + abs(x.escalation_impact), reverse=True)
    return impacts


def calculate_prompt_version_metrics(
    sessions: List[Any],
) -> Dict[str, AgentVersionMetrics]:
    if not sessions:
        return {}
    
    prompt_data = defaultdict(lambda: {
        "total": 0,
        "resolved": 0,
        "escalated": 0,
        "converted": 0,
        "retained": 0,
        "csats": [],
    })
    
    for session in sessions:
        prompt_version = getattr(session, "prompt_version", None)
        if not prompt_version:
            continue
        
        data = prompt_data[prompt_version]
        data["total"] += 1
        
        outcome = getattr(session, "outcome", "unknown")
        if outcome == "resolved":
            data["resolved"] += 1
        elif outcome == "escalated":
            data["escalated"] += 1
        elif outcome == "converted":
            data["converted"] += 1
        elif outcome == "retained":
            data["retained"] += 1
        
        csat = getattr(session, "csat_score", 0)
        if csat:
            data["csats"].append(csat)
    
    results = {}
    for prompt_version, data in prompt_data.items():
        if data["total"] == 0:
            continue
        
        resolution_rate = data["resolved"] / data["total"]
        escalation_rate = data["escalated"] / data["total"]
        csat_avg = statistics.mean(data["csats"]) if data["csats"] else 0.0
        
        metrics = AgentVersionMetrics(
            version=prompt_version,
            total_sessions=data["total"],
            resolution_rate=resolution_rate,
            escalation_rate=escalation_rate,
            csat_avg=csat_avg,
            avg_latency_ms=0.0,
            avg_cost=0.0,
            outcome_distribution={
                "resolved": data["resolved"],
                "escalated": data["escalated"],
                "converted": data["converted"],
                "retained": data["retained"],
            },
        )
        results[prompt_version] = metrics
    
    return results
# history: feat: add outcome attributor for root cause mapping