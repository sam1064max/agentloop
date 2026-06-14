"""Analytics service for computing insights and recommendations."""
from collections import defaultdict
from typing import Any

from app.models.session import Session
from app.models.trace import Trace
from app.models.outcome import Outcome
from app.models.feedback import Feedback
from app.schemas.analytics import (
    PathAnalysis,
    OutcomeMetrics,
    AgentComparison,
    RootCauseInsight,
    RecommendationItem,
)


class AnalyticsService:
    """Service for analytics and insights generation."""

    def calculate_path_success(
        self,
        sessions: list[Session],
        traces: list[Trace],
    ) -> list[PathAnalysis]:
        """Find most/least successful workflow paths."""
        session_traces = defaultdict(list)
        for trace in traces:
            session_traces[trace.session_id].append(trace)

        path_data = defaultdict(lambda: {
            "total": 0,
            "success": 0,
            "latencies": [],
            "costs": [],
        })

        for session in sessions:
            session_trace_list = session_traces.get(session.id, [])
            if not session_trace_list:
                continue

            tool_sequence = []
            for trace in session_trace_list:
                if trace.tool_calls_json:
                    for tc in trace.tool_calls_json:
                        tool_sequence.append(tc.get("tool_name", "unknown"))

            path_key = " -> ".join(tool_sequence) if tool_sequence else "no_tools"

            path_data[path_key]["total"] += 1

            successful_calls = 0
            total_calls = 0
            for trace in session_trace_list:
                if trace.tool_calls_json:
                    for tc in trace.tool_calls_json:
                        total_calls += 1
                        if tc.get("success", True):
                            successful_calls += 1

                if trace.latency_ms is not None:
                    path_data[path_key]["latencies"].append(trace.latency_ms)
                if trace.cost_usd is not None:
                    path_data[path_key]["costs"].append(trace.cost_usd)

            if total_calls > 0:
                success_rate = successful_calls / total_calls
                path_data[path_key]["success"] += success_rate

        path_analysis = []
        for path, data in path_data.items():
            if data["total"] == 0:
                continue

            avg_latency = (
                sum(data["latencies"]) / len(data["latencies"])
                if data["latencies"]
                else None
            )
            avg_cost = (
                sum(data["costs"]) / len(data["costs"])
                if data["costs"]
                else None
            )

            path_analysis.append(PathAnalysis(
                path=path,
                total_sessions=data["total"],
                success_count=int(data["success"] * data["total"] / 100) if data["success"] > 0 else 0,
                success_rate=data["success"] / data["total"] if data["total"] > 0 else 0,
                avg_latency_ms=avg_latency,
                avg_cost_usd=avg_cost,
            ))

        path_analysis.sort(key=lambda x: x.success_rate, reverse=True)
        return path_analysis

    def calculate_outcome_metrics(
        self,
        sessions: list[Session],
        feedbacks: list[Feedback],
        outcomes: list[Outcome],
    ) -> OutcomeMetrics | None:
        """Calculate CSAT, resolution rate, escalation rate."""
        if not sessions:
            return None

        session_ids = {s.id for s in sessions}

        session_outcomes = [o for o in outcomes if o.session_id in session_ids]
        session_feedbacks = [f for f in feedbacks if f.session_id in session_ids]

        outcome_counts = defaultdict(int)
        for outcome in session_outcomes:
            outcome_counts[outcome.outcome_type] += 1

        total = len(sessions)
        resolved = outcome_counts.get("resolved", 0)
        escalated = outcome_counts.get("escalated", 0)
        converted = outcome_counts.get("converted", 0)
        retained = outcome_counts.get("retained", 0)

        avg_csat = None
        if session_feedbacks:
            ratings = [f.rating for f in session_feedbacks]
            avg_csat = sum(ratings) / len(ratings)

        return OutcomeMetrics(
            total_sessions=total,
            resolved_count=resolved,
            escalated_count=escalated,
            converted_count=converted,
            retained_count=retained,
            resolution_rate=resolved / total if total > 0 else 0,
            escalation_rate=escalated / total if total > 0 else 0,
            conversion_rate=converted / total if total > 0 else 0,
            retention_rate=retained / total if total > 0 else 0,
            avg_csat=avg_csat,
        )

    def calculate_agent_comparison(
        self,
        sessions: list[Session],
        traces: list[Trace],
        feedbacks: list[Feedback],
        outcomes: list[Outcome],
    ) -> list[AgentComparison]:
        """Compare agent versions performance."""
        session_to_version = {s.id: s.agent_version for s in sessions}
        version_to_sessions = defaultdict(set)
        for s in sessions:
            version_to_sessions[s.agent_version].add(s.id)

        version_traces = defaultdict(list)
        for trace in traces:
            if trace.session_id in session_to_version:
                version = session_to_version[trace.session_id]
                version_traces[version].append(trace)

        version_feedbacks = defaultdict(list)
        for feedback in feedbacks:
            if feedback.session_id in session_to_version:
                version = session_to_version[feedback.session_id]
                version_feedbacks[version].append(feedback)

        agent_comparisons = []
        for version in version_to_sessions:
            traces_list = version_traces.get(version, [])
            feedbacks_list = version_feedbacks.get(version, [])
            session_count = len(version_to_sessions[version])

            if session_count == 0:
                continue

            latencies = [t.latency_ms for t in traces_list if t.latency_ms is not None]
            costs = [t.cost_usd for t in traces_list if t.cost_usd is not None]
            ratings = [f.rating for f in feedbacks_list if f.rating is not None]

            successful_calls = 0
            total_calls = 0
            for trace in traces_list:
                if trace.tool_calls_json:
                    for tc in trace.tool_calls_json:
                        total_calls += 1
                        if tc.get("success", True):
                            successful_calls += 1

            success_rate = successful_calls / total_calls if total_calls > 0 else 0

            agent_comparisons.append(AgentComparison(
                agent_version=version,
                session_count=session_count,
                success_rate=success_rate,
                avg_latency_ms=sum(latencies) / len(latencies) if latencies else None,
                avg_cost_usd=sum(costs) / len(costs) if costs else None,
                avg_csat=sum(ratings) / len(ratings) if ratings else None,
            ))

        agent_comparisons.sort(key=lambda x: x.success_rate, reverse=True)
        return agent_comparisons

    def generate_root_cause_insights(
        self,
        sessions: list[Session],
        traces: list[Trace],
        outcomes: list[Outcome],
    ) -> list[RootCauseInsight]:
        """Detect regressions and generate root cause insights."""
        insights = []

        session_traces = defaultdict(list)
        for trace in traces:
            session_traces[trace.session_id].append(trace)

        outcome_sessions = defaultdict(list)
        for outcome in outcomes:
            outcome_sessions[outcome.outcome_type].append(outcome.session_id)

        failed_sessions = set(outcome_sessions.get("escalated", []))
        successful_sessions = set(outcome_sessions.get("resolved", []))

        if failed_sessions:
            failed_traces_by_path = defaultdict(list)
            for session_id in failed_sessions:
                traces_list = session_traces.get(session_id, [])
                tool_sequence = []
                for trace in traces_list:
                    if trace.tool_calls_json:
                        for tc in trace.tool_calls_json:
                            tool_sequence.append(tc.get("tool_name", "unknown"))
                path = " -> ".join(tool_sequence) if tool_sequence else "no_tools"
                failed_traces_by_path[path].append(traces_list)

            for path, traces_list in failed_traces_by_path.items():
                if len(traces_list) >= 2:
                    insights.append(RootCauseInsight(
                        insight_type="failure_pattern",
                        description=f"Path '{path}' shows elevated failure rate",
                        affected_paths=[path],
                        impact_score=min(len(traces_list) / 10, 1.0),
                        recommendation=f"Review and optimize path '{path}' for better success rate",
                    ))

        outcome_by_version = defaultdict(lambda: defaultdict(int))
        for outcome in outcomes:
            for session in sessions:
                if session.id == outcome.session_id:
                    outcome_by_version[session.agent_version][outcome.outcome_type] += 1
                    break

        versions = list(outcome_by_version.keys())
        if len(versions) >= 2:
            for i, v1 in enumerate(versions):
                for v2 in versions[i + 1:]:
                    e1 = outcome_by_version[v1].get("escalated", 0)
                    t1 = sum(outcome_by_version[v1].values())
                    e2 = outcome_by_version[v2].get("escalated", 0)
                    t2 = sum(outcome_by_version[v2].values())

                    if t1 > 0 and t2 > 0:
                        rate1 = e1 / t1
                        rate2 = e2 / t2

                        if rate1 > rate2 * 1.5:
                            insights.append(RootCauseInsight(
                                insight_type="version_regression",
                                description=f"Version {v1} has higher escalation rate ({rate1:.1%}) vs {v2} ({rate2:.1%})",
                                affected_paths=[],
                                impact_score=abs(rate1 - rate2),
                                recommendation=f"Compare {v1} with {v2} to identify regression causes",
                            ))

        latencies_by_path = defaultdict(list)
        for trace in traces:
            if trace.latency_ms is not None and trace.tool_calls_json:
                tool_sequence = [
                    tc.get("tool_name", "unknown")
                    for tc in trace.tool_calls_json
                ]
                path = " -> ".join(tool_sequence)
                latencies_by_path[path].append(trace.latency_ms)

        for path, latencies in latencies_by_path.items():
            if len(latencies) >= 3:
                avg_latency = sum(latencies) / len(latencies)
                if avg_latency > 5000:
                    insights.append(RootCauseInsight(
                        insight_type="performance_degradation",
                        description=f"Path '{path}' has high average latency ({avg_latency:.0f}ms)",
                        affected_paths=[path],
                        impact_score=min(avg_latency / 10000, 1.0),
                        recommendation=f"Optimize performance for path '{path}'",
                    ))

        return insights

    def generate_recommendations(
        self,
        insights: list[RootCauseInsight],
    ) -> list[RecommendationItem]:
        """Prioritize and generate recommendations from insights."""
        recommendations = []

        for insight in insights:
            rec_type_map = {
                "failure_pattern": "fix",
                "version_regression": "fix",
                "performance_degradation": "optimization",
            }

            rec_type = rec_type_map.get(insight.insight_type, "optimization")

            priority = 1
            if insight.impact_score > 0.5:
                priority = 0
            elif insight.impact_score < 0.2:
                priority = 2

            recommendations.append(RecommendationItem(
                recommendation_type=rec_type,
                title=f"Address {insight.insight_type.replace('_', ' ')}",
                description=insight.description,
                impact=f"{insight.impact_score:.0%}" if insight.impact_score else None,
                confidence=0.8 if insight.recommendation else 0.5,
                priority=priority,
            ))

        recommendations.sort(key=lambda x: x.priority)
        return recommendations