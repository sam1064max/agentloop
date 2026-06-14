"""Outcome schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OutcomeType(str):
    """Outcome type values."""
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CONVERTED = "converted"
    RETAINED = "retained"


class OutcomeCreate(BaseModel):
    """Schema for creating an outcome."""
    session_id: str
    outcome_type: str = Field(..., pattern="^(resolved|escalated|converted|retained)$")
    value: float | None = None
    metadata: dict[str, Any] | None = None

    @field_validator("outcome_type")
    @classmethod
    def validate_outcome_type(cls, v: str) -> str:
        """Validate outcome type."""
        valid_types = {"resolved", "escalated", "converted", "retained"}
        if v not in valid_types:
            raise ValueError(f"outcome_type must be one of {valid_types}")
        return v


class OutcomeResponse(BaseModel):
    """Schema for outcome response."""
    id: UUID
    session_id: UUID
    outcome_type: str
    value: float | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}