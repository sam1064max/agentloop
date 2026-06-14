from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import logging

from .config import Settings
from .data_generator import generate_sessions, get_session_stats, sessions_to_dataframe
from .path_analyzer import analyze_paths, rank_paths_by_outcome, PathAnalysisResult
from .outcome_attributor import (
    calculate_outcome_metrics,
    compare_agent_versions,
    correlate_tool_failures,
    OutcomeMetrics,
)
from .root_cause_engine import (
    detect_regressions,
    find_correlated_failures,
    generate_recommendations,
    RootCauseInsight,
)

settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_cached_sessions = []
_session_stats = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Analytics service starting up...")
    yield
    logger.info("Analytics service shutting down...")


app = FastAPI(
    title="AgentLoop Analytics Service",
    description="Workflow analysis and outcome attribution for AI agents using DuckDB",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "analytics"}


@app.post("/generate-data")
async def generate_data(size: Optional[int] = None) -> Dict[str, Any]:
    global _cached_sessions, _session_stats
    
    if size is None:
        size = settings.sample_data_size
    
    if size < 100 or size > 1_000_000:
        raise HTTPException(status_code=400, detail="Size must be between 100 and 1,000,000")
    
    try:
        logger.info(f"Generating {size} sessions...")
        _cached_sessions = generate_sessions(size=size)
        _session_stats = get_session_stats(_cached_sessions)
        
        logger.info(f"Generated {len(_cached_sessions)} sessions")
        
        return {
            "status": "success",
            "sessions_generated": len(_cached_sessions),
            "stats": _session_stats,
        }
    except Exception as e:
        logger.error(f"Failed to generate data: {e}")
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")


@app.get("/analytics/paths", response_model=List[Dict[str, Any]])
async def get_path_analysis(
    min_count: Optional[int] = None,
    sort_by: Optional[str] = "volume",
) -> List[Dict[str, Any]]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        paths = analyze_paths(_cached_sessions)
        
        if min_count is not None:
            paths = [p for p in paths if p.count >= min_count]
        
        if sort_by:
            paths = rank_paths_by_outcome(paths, sort_by)
        
        return [p.__dict__ for p in paths]
    except Exception as e:
        logger.error(f"Path analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Path analysis failed: {str(e)}")


@app.get("/analytics/outcomes", response_model=Dict[str, Any])
async def get_outcome_metrics() -> Dict[str, Any]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        metrics = calculate_outcome_metrics(_cached_sessions)
        return metrics.to_dict()
    except Exception as e:
        logger.error(f"Outcome metrics calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Outcome metrics failed: {str(e)}")


@app.get("/analytics/versions", response_model=Dict[str, Dict[str, Any]])
async def get_version_comparison() -> Dict[str, Dict[str, Any]]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        version_metrics = compare_agent_versions(_cached_sessions)
        return {v: m.to_dict() for v, m in version_metrics.items()}
    except Exception as e:
        logger.error(f"Version comparison failed: {e}")
        raise HTTPException(status_code=500, detail=f"Version comparison failed: {str(e)}")


@app.get("/analytics/insights", response_model=List[Dict[str, Any]])
async def get_root_cause_insights(
    baseline_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        if baseline_size:
            baseline_sessions = generate_sessions(size=baseline_size, seed=43)
        else:
            half = len(_cached_sessions) // 2
            baseline_sessions = _cached_sessions[:half]
            current_sessions = _cached_sessions[half:]
            insights = detect_regressions(current_sessions, baseline_sessions)
            correlation_insights = find_correlated_failures(_cached_sessions, None)
            
            all_insights = insights + correlation_insights
            all_insights.sort(key=lambda x: x.impact_score, reverse=True)
            
            return [i.to_dict() for i in all_insights]
        
        half = len(_cached_sessions) // 2
        current_sessions = _cached_sessions[half:]
        
        insights = detect_regressions(current_sessions, baseline_sessions)
        correlation_insights = find_correlated_failures(_cached_sessions, None)
        
        all_insights = insights + correlation_insights
        all_insights.sort(key=lambda x: x.impact_score, reverse=True)
        
        return [i.to_dict() for i in all_insights]
    except Exception as e:
        logger.error(f"Root cause analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Root cause analysis failed: {str(e)}")


@app.get("/analytics/recommendations")
async def get_recommendations() -> Dict[str, Any]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        half = len(_cached_sessions) // 2
        baseline_sessions = _cached_sessions[:half]
        current_sessions = _cached_sessions[half:]
        
        insights = detect_regressions(current_sessions, baseline_sessions)
        correlation_insights = find_correlated_failures(_cached_sessions, None)
        
        all_insights = insights + correlation_insights
        recommendations = generate_recommendations(all_insights)
        
        return {
            "recommendations": recommendations,
            "insights_count": len(all_insights),
        }
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")


@app.get("/analytics/correlation")
async def get_tool_correlation() -> List[Dict[str, Any]]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        impacts = correlate_tool_failures(_cached_sessions, None)
        return [i.to_dict() for i in impacts]
    except Exception as e:
        logger.error(f"Tool correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tool correlation failed: {str(e)}")


@app.get("/analytics/summary")
async def get_analytics_summary() -> Dict[str, Any]:
    if not _cached_sessions:
        raise HTTPException(status_code=503, detail="No data available. Call /generate-data first.")
    
    try:
        outcome_metrics = calculate_outcome_metrics(_cached_sessions)
        version_metrics = compare_agent_versions(_cached_sessions)
        paths = analyze_paths(_cached_sessions)
        
        return {
            "total_sessions": len(_cached_sessions),
            "outcome_metrics": outcome_metrics.to_dict(),
            "version_count": len(version_metrics),
            "path_count": len(paths),
            "top_paths": [p.path_id for p in paths[:5]],
        }
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary failed: {str(e)}")