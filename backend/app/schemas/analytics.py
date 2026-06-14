"""Analytics schemas."""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PathAnalysis(BaseModel):
    """Schema for workflow path analysis."""
    path: str
    total_sessions: int
    success_count: int
    success_rate: float
    avg_latency_ms: float | None = None
    avg_cost_usd: float | None = None


class OutcomeMetrics(BaseModel):
    """Schema for outcome metrics."""
    total_sessions: int
    resolved_count: int
    escalated_count: int
    converted_count: int
    retained_count: int
    resolution_rate: float
    escalation_rate: float
    conversion_rate: float
    retention_rate: float
    avg_csat: float | None = None


class AgentComparison(BaseModel):
    """Schema for agent version comparison."""
    agent_version: str
    session_count: int
    success_rate: float
    avg_latency_ms: float | None = None
    avg_cost_usd: float | None = None
    avg_csat: float | None = None


class RootCauseInsight(BaseModel):
    """Schema for root cause insight."""
    insight_type: str
    description: str
    affected_paths: list[str] = Field(default_factory=list)
    impact_score: float
    recommendation: str | None = None


class RecommendationItem(BaseModel):
    """Schema for recommendation item."""
    recommendation_type: str
    title: str
    description: str | None = None
    impact: str | None = None
    confidence: float | None = None
    priority: int


class AnalyticsResponse(BaseModel):
    """Schema for analytics response."""
    path_analysis: list[PathAnalysis] = Field(default_factory=list)
    outcome_metrics: OutcomeMetrics | None = None
    agent_comparison: list[AgentComparison] = Field(default_factory=list)
    root_cause_insights: list[RootCauseInsight] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)