# Milestones: Phase 1 (Jan–Mar 2026)

| Milestone | Date | H3            | Description                                      | Key Deliverables |
|-----------|------|-----------------|---------------------------------------------------|-------------------|
| M-1       | Jan 15 | Foundation Setup | Scaffold repo, CI/CD, OTel collector, Postgres, DuckDB | Dockerfile / docker-compose, GitHub Actions with tests, 80% coverage, basic FastAPI server handling happy path, ingest test suite |
| M-2       | Jan 31 | Ingestion Working | 100k sessions ingested daily, structured and versioned | Trace schema validated by Pydantic, OTel pipeline stable, version metadata attached per-trace |
| M-3       | Feb 14 | Outcome Attribution | Every trace mapped to a business outcome (CSAT, resolution, conversion) | Outcome registry in YAML (config-driven), Postgres fact tables, DuckDB latency for ad-hoc queries, span enrichment with outcome IDs |
| M-4       | Feb 28 | Feedback Loop | Feedback classified pass at >90% accuracy     | Explicit feedback endpoint, Implicit heuristics module, Classification model (training + evaluation), Correlation query between feedback and results |
| M-5       | Mar 14 | Analytics & Insights | Dashboard operational with drilled  traces | KPI endpoint (6 KPIs), React dashboard rendering, workflow comparison, root-cause insights published |
| M-6       | Mar 31 | Prod-Ready & Review | Performance, security, documentation | Prometheus/Grafana monitoring, P0 bugs closed, User guide for the executive dashboard, Architecture decision records (ADRs) updated |

## Success Criteria for Phase 1
- 100,000 traces ingested without loss
- Outcome attribution accuracy validated with blind-sample audit
- Dashboard renders all KPIs linked to traces < 1s
- All dependencies documented, ADRs created
