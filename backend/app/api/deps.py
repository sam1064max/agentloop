"""API dependencies."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token


async def get_current_session(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AsyncSession:
    """Get database session dependency."""
    return db


def get_pagination_params(
    skip: int = 0,
    limit: int = 100,
) -> dict[str, int]:
    """Get pagination parameters."""
    return {"skip": skip, "limit": min(limit, 1000)}


def get_session_or_404(session_id: str, db: AsyncSession):
    """Validate session exists or raise 404."""
    from app.models.session import Session
    from sqlalchemy import select

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Session {session_id} not found",
    )