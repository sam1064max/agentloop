"""Sessions API routes."""
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.trace import Trace
from app.models.feedback import Feedback
from app.models.outcome import Outcome

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionListItem(BaseModel):
    """Schema for session list item."""
    id: UUID
    session_id: str
    agent_version: str
    prompt_version: str
    created_at: datetime
    metadata: dict | None = None
    trace_count: int = 0
    has_feedback: bool = False
    has_outcome: bool = False

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    """Schema for session list response."""
    total: int
    skip: int
    limit: int
    sessions: list[SessionListItem]


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    agent_version: str | None = None,
    prompt_version: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> SessionListResponse:
    """List sessions with pagination and filters."""
    query = select(Session)
    count_query = select(func.count(Session.id))

    if agent_version:
        query = query.where(Session.agent_version == agent_version)
        count_query = count_query.where(Session.agent_version == agent_version)
    if prompt_version:
        query = query.where(Session.prompt_version == prompt_version)
        count_query = count_query.where(Session.prompt_version == prompt_version)
    if start_date:
        query = query.where(Session.created_at >= start_date)
        count_query = count_query.where(Session.created_at >= start_date)
    if end_date:
        query = query.where(Session.created_at <= end_date)
        count_query = count_query.where(Session.created_at <= end_date)

    query = query.order_by(Session.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    sessions = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    trace_count_query = (
        select(Trace.session_id, func.count(Trace.id).label("count"))
        .group_by(Trace.session_id)
    )
    trace_counts = {row.session_id: row.count for row in (await db.execute(trace_count_query)).all()}

    feedback_query = (
        select(Feedback.session_id)
        .distinct()
    )
    sessions_with_feedback = {row.session_id for row in (await db.execute(feedback_query)).all()}

    outcome_query = (
        select(Outcome.session_id)
        .distinct()
    )
    sessions_with_outcome = {row.session_id for row in (await db.execute(outcome_query)).all()}

    session_items = [
        SessionListItem(
            id=s.id,
            session_id=s.session_id,
            agent_version=s.agent_version,
            prompt_version=s.prompt_version,
            created_at=s.created_at,
            metadata=s.metadata_json,
            trace_count=trace_counts.get(s.id, 0),
            has_feedback=s.id in sessions_with_feedback,
            has_outcome=s.id in sessions_with_outcome,
        )
        for s in sessions
    ]

    return SessionListResponse(
        total=total,
        skip=skip,
        limit=limit,
        sessions=session_items,
    )


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Session:
    """Get a session by session_id."""
    result = await db.execute(select(Session).where(Session.session_id == session_id))
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found",
        )

    return session