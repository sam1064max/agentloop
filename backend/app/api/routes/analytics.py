"""Analytics API routes."""
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.trace import Trace
from app.models.feedback import Feedback
from app.models.outcome import Outcome
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    agent_version: str | None = Query(None),
) -> AnalyticsResponse:
    """Get analytics data including path analysis, outcome metrics, and recommendations."""
    query = select(Session)
    count_query = select(func.count(Session.id))

    if start_date:
        query = query.where(Session.created_at >= start_date)
        count_query = count_query.where(Session.created_at >= start_date)
    if end_date:
        query = query.where(Session.created_at <= end_date)
        count_query = count_query.where(Session.created_at <= end_date)
    if agent_version:
        query = query.where(Session.agent_version == agent_version)
        count_query = count_query.where(Session.agent_version == agent_version)

    sessions_result = await db.execute(query)
    sessions = sessions_result.scalars().all()

    if not sessions:
        return AnalyticsResponse(
            path_analysis=[],
            outcome_metrics=None,
            agent_comparison=[],
            root_cause_insights=[],
            recommendations=[],
            generated_at=datetime.utcnow(),
        )

    session_ids = [s.id for s in sessions]

    traces_result = await db.execute(
        select(Trace).where(Trace.session_id.in_(session_ids))
    )
    traces = traces_result.scalars().all()

    feedbacks_result = await db.execute(
        select(Feedback).where(Feedback.session_id.in_(session_ids))
    )
    feedbacks = feedbacks_result.scalars().all()

    outcomes_result = await db.execute(
        select(Outcome).where(Outcome.session_id.in_(session_ids))
    )
    outcomes = outcomes_result.scalars().all()

    analytics_service = AnalyticsService()

    path_analysis = analytics_service.calculate_path_success(sessions, traces)
    outcome_metrics = analytics_service.calculate_outcome_metrics(
        sessions, feedbacks, outcomes
    )
    agent_comparison = analytics_service.calculate_agent_comparison(
        sessions, traces, feedbacks, outcomes
    )
    root_cause_insights = analytics_service.generate_root_cause_insights(
        sessions, traces, outcomes
    )
    recommendations = analytics_service.generate_recommendations(root_cause_insights)

    return AnalyticsResponse(
        path_analysis=path_analysis,
        outcome_metrics=outcome_metrics,
        agent_comparison=agent_comparison,
        root_cause_insights=root_cause_insights,
        recommendations=recommendations,
        generated_at=datetime.utcnow(),
    )