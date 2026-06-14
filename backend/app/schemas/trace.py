"""Trace schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ToolCallCreate(BaseModel):
    """Schema for creating a tool call."""
    tool_name: str
    tool_input: dict[str, Any] | None = None
    tool_output: dict[str, Any] | None = None
    success: bool = True
    duration_ms: float | None = None


class TraceCreate(BaseModel):
    """Schema for creating a trace."""
    session_id: str
    prompt: str
    response: str
    tool_calls: list[ToolCallCreate] | None = None
    timings: dict[str, Any] | None = None
    latency_ms: float | None = None
    cost_usd: float | None = None


class TraceResponse(BaseModel):
    """Schema for trace response."""
    id: UUID
    session_id: UUID
    prompt: str
    response: str
    tool_calls: list[dict[str, Any]] | None = None
    timings: dict[str, Any] | None = None
    latency_ms: float | None = None
    cost_usd: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TraceWithSession(BaseModel):
    """Schema for trace with session info."""
    id: UUID
    session_id: str
    prompt: str
    response: str
    tool_calls: list[dict[str, Any]] | None = None
    timings: dict[str, Any] | None = None
    latency_ms: float | None = None
    cost_usd: float | None = None
    created_at: datetime
    agent_version: str | None = None
    prompt_version: str | None = None

    model_config = {"from_attributes": True}