# GitHub Issues

## Epic 1: Trace Collection Pipeline (#1)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 2  | Trace ingestion service for FastAPI       | trace,infrastrcture,core,triage       | unassigned |
| 3  | OpenTelemetry collector configuration       | trace,observability,core               | unassigned |
| 4  | Session schema validation with Pydantic       | trace,core,validation             | unassigned |
| 5  | Version metadata on every trace              | trace,core,versioning                | unassigned |

## Epic 2: Outcome Tracking System (#6)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 8  | Outcome registry design (YAML-based)          | outcome,core,design                   | unassigned |
| 9  | PostgreSQL schema for outcomes                | outcome,database,core                 | unassigned |
| 10 | DuckDB curation layer for ad-hoc queries      | outcome,analytics,core,triage         | unassigned |
| 11 | OpenTelemetry span enrichment with outcome IDs| outcome,observability,core            | unassigned |

## Epic 3: Feedback Collection & Classification (#12)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 14 | Explicit feedback endpoint (thumbs/survey)     | feedback,web,ml                       | unassigned |
| 15 | Implicit feedback heuristics module            | feedback,core,ml,triage               | unassigned |
| 16 | Classification model training pipeline         | feedback,ml,devops                     | unassigned |
| 17 | Feedback/results correlation query             | feedback,analytics                     | unassigned |

## Epic 4: Workflow Analytics (#18)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 20 | KPI endpoint (6 primary metrics)                 | analytics,web,core                      | unassigned |
| 21 | Dashboard trace drill-down                     | analytics,frontend,,triage              | unassigned |
| 22 | Workflow comparison table                     | analytics,frontend,core               | unassigned |
| 23 | Alert thresholds per workflow                  | analytics,ops,triage                     | unassigned |

## Epic 5: Root Cause Insights (#24)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 26 | Trace clustering algorithm                     | insights,ml,core,triage               | unassigned |
| 27 | Correlation engine for bad outcomes           | insights,ml,core                       | unassigned |
| 28 | Insight drill-down to trace list               | insights,frontend,analytics             | unassigned |
| 29 | Scheduled insight generation (cron + Celery)   | insights,devops,ops                   | unassigned |

## Epic 6: Executive Dashboard (#30)

| # | Title | Labels | Assignee |
|---|-------|--------|----------|
| 32 | React scaffold with Vite + Tailwind + Recharts | frontend,setup,,triage                 | unassigned |
| 33 | KPI chart component (6 recharts)              | frontend,component,,triage             | unassigned |
| 34 | Trace deep-link modal                         | frontend,component,,triage             | unassigned |
| 35 | Auth / RBAC wiring for read-only or admin      | frontend,security,triage               | unassigned |

---

### Easiest / Warm-up
2, 8, 9 (Trace service, outcome YAML, outcome DB)

### Dependencies
32 → 33 → 34 (React scaffold before charts before drill-down modal)

### Notes
All issues lack explicit assignees as of now.
Use GitHub sub-issues feature for children to keep epics organized.
