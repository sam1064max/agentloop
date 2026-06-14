"""Trace service for trace-related business logic."""
import json
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.trace import Trace
from app.models.tool_call import ToolCall


class TraceService:
    """Service for trace operations."""

    @staticmethod
    async def get_traces_by_session(
        db: AsyncSession,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Trace]:
        """Get traces for a session."""
        session_result = await db.execute(
            select(Session).where(Session.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()

        if not session:
            return []

        result = await db.execute(
            select(Trace)
            .where(Trace.session_id == session.id)
            .order_by(Trace.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_tool_calls_by_trace(
        db: AsyncSession,
        trace_id: UUID,
    ) -> list[ToolCall]:
        """Get tool calls for a trace."""
        result = await db.execute(
            select(ToolCall).where(ToolCall.trace_id == trace_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def calculate_session_metrics(
        db: AsyncSession,
        session_id: str,
    ) -> dict:
        """Calculate aggregated metrics for a session."""
        traces = await TraceService.get_traces_by_session(db, session_id)

        if not traces:
            return {
                "trace_count": 0,
                "avg_latency_ms": None,
                "total_cost_usd": None,
                "total_tool_calls": 0,
                "success_rate": None,
            }

        latencies = [t.latency_ms for t in traces if t.latency_ms is not None]
        costs = [t.cost_usd for t in traces if t.cost_usd is not None]

        all_tool_calls = []
        for trace in traces:
            if trace.tool_calls_json:
                all_tool_calls.extend(trace.tool_calls_json)

        successful_calls = sum(1 for tc in all_tool_calls if tc.get("success", True))
        success_rate = successful_calls / len(all_tool_calls) if all_tool_calls else None

        return {
            "trace_count": len(traces),
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else None,
            "total_cost_usd": sum(costs) if costs else None,
            "total_tool_calls": len(all_tool_calls),
            "success_rate": success_rate,
        }