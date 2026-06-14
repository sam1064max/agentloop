"""Outcome engine for processing and analyzing outcomes."""
from collections import defaultdict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.trace import Trace
from app.models.outcome import Outcome
from app.models.feedback import Feedback


class OutcomeEngine:
    """Engine for processing business outcomes."""

    @staticmethod
    def categorize_outcome(outcome_type: str) -> str:
        """Categorize outcome into positive, negative, or neutral."""
        positive = {"resolved", "converted", "retained"}
        negative = {"escalated"}

        if outcome_type in positive:
            return "positive"
        elif outcome_type in negative:
            return "negative"
        return "neutral"

    @staticmethod
    def calculate_outcome_value(
        outcome_type: str,
        base_value: float | None,
        feedback_score: float | None = None,
    ) -> float | None:
        """Calculate weighted outcome value."""
        if base_value is None and feedback_score is None:
            return None

        outcome_multipliers = {
            "resolved": 1.0,
            "converted": 1.5,
            "retained": 0.8,
            "escalated": -0.5,
        }

        multiplier = outcome_multipliers.get(outcome_type, 1.0)

        if feedback_score is not None and base_value is not None:
            return base_value * multiplier * (feedback_score / 5.0)
        elif base_value is not None:
            return base_value * multiplier
        elif feedback_score is not None:
            return feedback_score * multiplier

        return None

    @staticmethod
    def get_session_outcome_summary(
        session_id: UUID,
        outcomes: list[Outcome],
        feedbacks: list[Feedback],
    ) -> dict:
        """Get outcome summary for a session."""
        session_outcomes = [o for o in outcomes if o.session_id == session_id]
        session_feedbacks = [f for f in feedbacks if f.session_id == session_id]

        if not session_outcomes:
            return {
                "has_outcome": False,
                "primary_outcome": None,
                "total_value": None,
                "csat": None,
            }

        outcome_types = defaultdict(int)
        total_value = 0.0
        has_value = False

        for outcome in session_outcomes:
            outcome_types[outcome.outcome_type] += 1
            if outcome.value is not None:
                total_value += outcome.value
                has_value = True

        primary_outcome = max(outcome_types, key=outcome_types.get)

        avg_rating = None
        if session_feedbacks:
            ratings = [f.rating for f in session_feedbacks]
            avg_rating = sum(ratings) / len(ratings)

        return {
            "has_outcome": True,
            "primary_outcome": primary_outcome,
            "total_value": total_value if has_value else None,
            "csat": avg_rating,
        }

    @staticmethod
    def detect_regression(
        current_metrics: dict,
        baseline_metrics: dict,
        threshold: float = 0.1,
    ) -> dict | None:
        """Detect if current metrics show regression from baseline."""
        checks = [
            ("success_rate", "lower"),
            ("avg_latency_ms", "higher"),
            ("escalation_rate", "higher"),
        ]

        regressions = []

        for metric, direction in checks:
            current = current_metrics.get(metric)
            baseline = baseline_metrics.get(metric)

            if current is None or baseline is None or baseline == 0:
                continue

            change_pct = (current - baseline) / baseline

            if direction == "lower" and change_pct < -threshold:
                regressions.append({
                    "metric": metric,
                    "baseline": baseline,
                    "current": current,
                    "change_pct": change_pct,
                })
            elif direction == "higher" and change_pct > threshold:
                regressions.append({
                    "metric": metric,
                    "baseline": baseline,
                    "current": current,
                    "change_pct": change_pct,
                })

        if regressions:
            return {
                "regressions": regressions,
                "severity": "high" if len(regressions) >= 2 else "medium",
            }

        return None