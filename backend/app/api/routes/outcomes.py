"""Outcomes API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.outcome import Outcome
from app.schemas.outcome import OutcomeCreate, OutcomeResponse

router = APIRouter(prefix="/outcomes", tags=["outcomes"])


@router.post("", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED)
async def create_outcome(
    outcome_data: OutcomeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Outcome:
    """Ingest outcome with session_id, outcome_type, value, and metadata."""
    result = await db.execute(
        select(Session).where(Session.session_id == outcome_data.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {outcome_data.session_id} not found",
        )

    outcome = Outcome(
        session_id=session.id,
        outcome_type=outcome_data.outcome_type,
        value=outcome_data.value,
        metadata_json=outcome_data.metadata,
    )
    db.add(outcome)
    await db.commit()
    await db.refresh(outcome)

    return outcome


@router.get("/{outcome_id}", response_model=OutcomeResponse)
async def get_outcome(
    outcome_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Outcome:
    """Get outcome by ID."""
    result = await db.execute(select(Outcome).where(Outcome.id == outcome_id))
    outcome = result.scalar_one_or_none()

    if not outcome:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Outcome {outcome_id} not found",
        )

    return outcome