# GitHub Epics

## Epic 1: Trace Collection Pipeline
**Labels:** `epic`, `trace`, `core`

### Description
Build ingestion pipeline for 100k sessions, multiple agent versions, prompts, and workflow paths. Collect full OpenTelemetry traces with semantic conventions for AI-agent spans.

### Acceptance Criteria
- [ ] Ingest 100k sessions/day without loss
- [ ] Support versioning of prompts, agents, and workflows
- [ ] Enrich traces with business outcome IDs
- [ ] CLI tool validates schema on ingestion

### Linked Issues
- #2 Trace ingestion service for FastAPI
- #3 OpenTelemetry collector config
- #4 Session schema validation with Pydantic
- #5 Version metadata on every trace

---

## Epic 2: Outcome Tracking System
**Labels:** `epic`, `outcome`, `core`

### Description
Map every session to a business outcome (CSAT, resolution, conversion). Allow analysts to define new outcome dimensions without code changes.

### Acceptance Criteria
- [ ] Extensible outcome registry via config
- [ ] Outcome attribution to specific trace spans
- [ ] Support objective + subjective outcomes
- [ ] BI-ready fact table in DuckDB / PostgreSQL

### Linked Issues
- #8 Outcome registry design
- #9 Postgres schema for outcomes
- #10 DuckDB curation layer for ad-hoc queries
- #11 OpenTelemetry span enrichment with outcome IDs

---

## Epic 3: Feedback Collection & Classification
**Labels:** `epic`, `feedback`, `ml`

### Description
Collect explicit and implicit feedback, then classify with a lightweight NLP model. Correlate feedback with traces for root-cause analysis.

### Acceptance Criteria
- [ ] REST endpoints for explicit feedback (thumbs, survey)
- [ ] Implicit feedback heuristics (ticket-reopen, refund)
- [ ] Classification model scores each session
- [ >90% satisfaction-class accuracy on validation set

### Linked Issues
- #14 Explicit feedback endpoint
- #15 Implicit feedback heuristics module
- #16 Classification model training pipeline
- #17 Feedback/results correlation query

---

## Epic 4: Workflow Analytics
**Labels:** `epic`, `analytics`, `reporting`

### Description
Dashboard and API showing per-workflow conversion, CSAT, drop-off, and resolution. Enable drill-down from 10k-meter view to single trace.

### Acceptance Criteria
- [ ] All 6 Phase-1 KPIs exposed via API
- [ ] Executive dashboard renders all linked traces for a metric
- [ ] Aggregate latency and error rollups
- [ ] Workflow-path comparison tool

### Linked Issues
- #20 KPI endpoint (conversion, CSAT, drop-off, resolution, latency, error)
- #21 Trace drill-down from dashboard
- #22 Workflow comparison table
- #23 Alert thresholds per workflow

---

## Epic 5: Root Cause Insights
**Labels:** `epic`, `insights`, `ml`

### Description
Identify likely root causes by clustering traces linked to bad outcomes. Show top attribute groups correlated with failure.

### Acceptance Criteria
- [ ] Cluster traces by shared attributes (prompt, step, agent version)
- [ ] Surface top failure correlations with statistical significance
- [ ] One-click from an insight to filtered trace list
- [ ] Export insight reports as JSON

### Linked Issues
- #26 Trace clustering algorithm
- #27 Correlation engine for bad outcomes
- #28 Insight drill-down to traces
- #29 Scheduled insight generation

---

## Epic 6: Executive Dashboard
**Labels:** `epic`, `dashboard`, `frontend`

### Description
Single-page React/Vite app with Recharts visualizing Phase-1 KPIs. Tailwind for styling, dark mode, and 60 fps updates.

### Acceptance Criteria
- [ ] Renders on desktop and mobile
- [ ] Links every metric to source traces
- [ ] Vary date range with 100k sessions in <1s
- [ ] Role-based access (read-only vs admin)

### Linked Issues
- #32 React scaffold with Vite + Tailwind + Recharts
- #33 KPI chart component (6 metrics)
- #34 Trace deep-link modal
- #35 Auth/role wiring
