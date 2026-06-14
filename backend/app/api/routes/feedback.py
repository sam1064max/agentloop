"""Feedback API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Feedback:
    """Ingest feedback with session_id, rating (1-5), comment, and tags."""
    result = await db.execute(
        select(Session).where(Session.session_id == feedback_data.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {feedback_data.session_id} not found",
        )

    feedback = Feedback(
        session_id=session.id,
        rating=feedback_data.rating,
        comment=feedback_data.comment,
        tags=feedback_data.tags,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return feedback


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Feedback:
    """Get feedback by ID."""
    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feedback {feedback_id} not found",
        )

    return feedback