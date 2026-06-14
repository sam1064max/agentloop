"""Feedback schemas."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FeedbackCreate(BaseModel):
    """Schema for creating feedback."""
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None
    tags: list[str] | None = None

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Validate rating is between 1 and 5."""
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    id: UUID
    session_id: UUID
    rating: int
    comment: str | None = None
    tags: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}