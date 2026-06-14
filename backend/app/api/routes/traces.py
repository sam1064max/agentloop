"""Traces API routes."""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.session import Session
from app.models.trace import Trace
from app.models.tool_call import ToolCall
from app.schemas.trace import TraceCreate, TraceResponse

router = APIRouter(prefix="/traces", tags=["traces"])


@router.post("", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
async def create_trace(
    trace_data: TraceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Trace:
    """Ingest a new trace with session_id, prompt, response, tool_calls, and timings."""
    result = await db.execute(
        select(Session).where(Session.session_id == trace_data.session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        session = Session(
            session_id=trace_data.session_id,
            agent_version="unknown",
            prompt_version="unknown",
        )
        db.add(session)
        await db.flush()

    trace = Trace(
        session_id=session.id,
        prompt=trace_data.prompt,
        response=trace_data.response,
        tool_calls_json=[tc.model_dump() for tc in trace_data.tool_calls] if trace_data.tool_calls else None,
        timings_json=trace_data.timings,
        latency_ms=trace_data.latency_ms,
        cost_usd=trace_data.cost_usd,
    )
    db.add(trace)
    await db.flush()

    if trace_data.tool_calls:
        for tc_data in trace_data.tool_calls:
            tool_call = ToolCall(
                trace_id=trace.id,
                tool_name=tc_data.tool_name,
                tool_input_json=tc_data.tool_input,
                tool_output_json=tc_data.tool_output,
                success=tc_data.success,
                duration_ms=tc_data.duration_ms,
            )
            db.add(tool_call)

    await db.commit()
    await db.refresh(trace)

    return trace


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(
    trace_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Trace:
    """Get a trace by ID."""
    result = await db.execute(select(Trace).where(Trace.id == trace_id))
    trace = result.scalar_one_or_none()

    if not trace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace {trace_id} not found",
        )

    return trace