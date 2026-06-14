import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass, field
import uuid


AGENT_VERSIONS = ["v1.0", "v1.1", "v1.2", "v2.0"]
PROMPT_VERSIONS = [f"prompt_v{i}" for i in range(1, 9)]

WORKFLOW_PATHS = {
    "search_crm_kb_respond": {
        "steps": ["search", "crm_lookup", "kb_search", "respond"],
        "success_rate": 0.92,
        "base_latency": 220,
    },
    "search_crm_escalate": {
        "steps": ["search", "crm_lookup", "escalate"],
        "success_rate": 0.38,
        "base_latency": 180,
    },
    "search_kb_respond": {
        "steps": ["search", "kb_search", "respond"],
        "success_rate": 0.78,
        "base_latency": 160,
    },
    "search_escalate": {
        "steps": ["search", "escalate"],
        "success_rate": 0.45,
        "base_latency": 120,
    },
    "crm_search_kb_respond": {
        "steps": ["crm_lookup", "search", "kb_search", "respond"],
        "success_rate": 0.85,
        "base_latency": 240,
    },
    "crm_kb_respond": {
        "steps": ["crm_lookup", "kb_search", "respond"],
        "success_rate": 0.75,
        "base_latency": 200,
    },
    "kb_search_respond": {
        "steps": ["kb_search", "search", "respond"],
        "success_rate": 0.68,
        "base_latency": 170,
    },
}

TOOL_CALLS = ["search", "crm_lookup", "kb_search", "escalate", "respond", "transfer"]

OUTCOMES = {
    "resolved": 0.60,
    "escalated": 0.25,
    "converted": 0.10,
    "retained": 0.05,
}

TOOL_FAILURE_RATE = 0.05

START_DATE = datetime(2026, 1, 20)
END_DATE = datetime(2026, 3, 20)
DAYS_SPAN = (END_DATE - START_DATE).days


@dataclass
class Session:
    session_id: str
    agent_version: str
    prompt_version: str
    path_id: str
    steps: List[str]
    outcome: str
    csat_score: int
    latency_ms: int
    cost: float
    tool_failures: List[str]
    timestamp: datetime
    user_id: str
    conversation_duration_sec: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "agent_version": self.agent_version,
            "prompt_version": self.prompt_version,
            "path_id": self.path_id,
            "steps": ",".join(self.steps),
            "outcome": self.outcome,
            "csat_score": self.csat_score,
            "latency_ms": self.latency_ms,
            "cost": self.cost,
            "tool_failures": ",".join(self.tool_failures) if self.tool_failures else "",
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "conversation_duration_sec": self.conversation_duration_sec,
        }


def _weighted_choice(choices: Dict[str, float]) -> str:
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights, k=1)[0]


def _generate_session_id(timestamp: datetime, index: int) -> str:
    raw = f"{timestamp.isoformat()}-{index}-{random.random()}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def _assign_outcome(path_id: str) -> str:
    path_info = WORKFLOW_PATHS.get(path_id)
    if path_info and random.random() < path_info["success_rate"]:
        return "resolved"
    
    if random.random() < 0.60:
        return "escalated"
    elif random.random() < 0.70:
        return "converted"
    else:
        return "retained"


def _generate_csat(outcome: str, base_latency: int) -> int:
    if outcome == "escalated":
        base_score = random.randint(1, 3)
    elif outcome == "resolved":
        if base_latency < 200:
            base_score = random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6], k=1)[0]
        else:
            base_score = random.choices([2, 3, 4, 5], weights=[0.15, 0.35, 0.35, 0.15], k=1)[0]
    elif outcome == "converted":
        base_score = random.choices([4, 5], weights=[0.4, 0.6], k=1)[0]
    else:
        base_score = random.randint(2, 4)
    
    return base_score


def _inject_tool_failures(steps: List[str]) -> tuple[List[str], List[str]]:
    failures = []
    modified_steps = []
    
    for step in steps:
        modified_steps.append(step)
        if random.random() < TOOL_FAILURE_RATE:
            failures.append(step)
            retry_step = f"{step}_retry"
            modified_steps.append(retry_step)
    
    return modified_steps, failures


def _calculate_cost(steps: List[str], tool_failures: List[str]) -> float:
    base_cost_per_step = 0.002
    failure_penalty = 0.001
    
    cost = len(steps) * base_cost_per_step
    cost += len(tool_failures) * failure_penalty
    
    return round(cost, 4)


def _distribute_versions() -> str:
    weights = [0.15, 0.25, 0.35, 0.25]
    return random.choices(AGENT_VERSIONS, weights=weights, k=1)[0]


def _distribute_timestamps(size: int) -> List[datetime]:
    timestamps = []
    interval_seconds = (DAYS_SPAN * 24 * 60 * 60) / size
    
    for i in range(size):
        offset_seconds = int(i * interval_seconds + random.uniform(-interval_seconds * 0.5, interval_seconds * 0.5))
        offset_seconds = max(0, min(offset_seconds, DAYS_SPAN * 24 * 60 * 60))
        ts = START_DATE + timedelta(seconds=offset_seconds)
        timestamps.append(ts)
    
    random.shuffle(timestamps)
    return timestamps


def generate_sessions(size: int = 100_000, seed: int = 42) -> List[Session]:
    random.seed(seed)
    
    path_weights = {pid: 1.0 for pid in WORKFLOW_PATHS.keys()}
    path_weights["search_crm_kb_respond"] = 3.0
    path_weights["search_crm_escalate"] = 0.5
    path_weights["search_kb_respond"] = 2.0
    path_weights["search_escalate"] = 0.8
    path_weights["crm_search_kb_respond"] = 1.5
    path_weights["crm_kb_respond"] = 1.2
    path_weights["kb_search_respond"] = 1.0
    
    timestamps = _distribute_timestamps(size)
    
    sessions = []
    
    for i in range(size):
        session_id = _generate_session_id(timestamps[i], i)
        agent_version = _distribute_versions()
        prompt_version = random.choice(PROMPT_VERSIONS)
        
        path_id = _weighted_choice(path_weights)
        path_info = WORKFLOW_PATHS[path_id]
        steps = path_info["steps"].copy()
        
        steps_with_failures, tool_failures = _inject_tool_failures(steps)
        
        outcome = _assign_outcome(path_id)
        
        latency_variation = random.gauss(0, path_info["base_latency"] * 0.2)
        latency = max(50, int(path_info["base_latency"] + latency_variation))
        
        csat = _generate_csat(outcome, latency)
        
        cost = _calculate_cost(steps_with_failures, tool_failures)
        
        conversation_duration = random.randint(30, latency // 10 + 600)
        
        user_id = f"user_{hashlib.md5(str(i).encode()).hexdigest()[:8]}"
        
        session = Session(
            session_id=session_id,
            agent_version=agent_version,
            prompt_version=prompt_version,
            path_id=path_id,
            steps=steps_with_failures,
            outcome=outcome,
            csat_score=csat,
            latency_ms=latency,
            cost=cost,
            tool_failures=tool_failures,
            timestamp=timestamps[i],
            user_id=user_id,
            conversation_duration_sec=conversation_duration,
        )
        sessions.append(session)
    
    return sessions


def sessions_to_dataframe(sessions: List[Session]):
    try:
        import pandas as pd
        return pd.DataFrame([s.to_dict() for s in sessions])
    except ImportError:
        import polars as pl
        return pl.DataFrame([s.to_dict() for s in sessions])


def get_session_stats(sessions: List[Session]) -> Dict[str, Any]:
    if not sessions:
        return {}
    
    outcomes_count = {}
    versions_count = {}
    paths_count = {}
    
    for s in sessions:
        outcomes_count[s.outcome] = outcomes_count.get(s.outcome, 0) + 1
        versions_count[s.agent_version] = versions_count.get(s.agent_version, 0) + 1
        paths_count[s.path_id] = paths_count.get(s.path_id, 0) + 1
    
    latencies = [s.latency_ms for s in sessions]
    csats = [s.csat_score for s in sessions]
    
    return {
        "total_sessions": len(sessions),
        "outcome_distribution": outcomes_count,
        "version_distribution": versions_count,
        "path_distribution": paths_count,
        "avg_latency_ms": sum(latencies) / len(latencies),
        "avg_csat": sum(csats) / len(csats),
        "total_cost": sum(s.cost for s in sessions),
    }