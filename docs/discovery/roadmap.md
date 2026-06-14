# Product Roadmap: AgentLoop

## Vision
Connect AI agent traces to real business outcomes for production support teams.

## Phase 1: Closed-Loop Outcome Intelligence (Jan–Mar 2026)
- **Goal**: Production-quality proof-of-concept for customer-support agents.
- **Deliverables**:
  - Trace Collection: 100k sessions, multi-version, multi-prompt tracks.
  - Outcome Tracking: CSAT, resolution, conversion mapped to sessions.
  - Feedback Collection: Explicit (survey) and implicit (tickets/reopens).
  - Workflow Analytics: Per-workflow conversion, drop-off, error rates.
  - Root Cause Insights: Failure clustering and statistical correlation.
  - Executive Dashboard: Single-page React app linked to source traces.
- **Tech**: Python 3.12, FastAPI, SQLAlchemy, Pydantic, PostgreSQL, DuckDB, OpenTelemetry, Prometheus, Grafana, React, Vite, TypeScript, Tailwind, Recharts, Docker, GitHub Actions.
- **Target**: Customer Support Agents.

## Phase 2: Expansion API (Apr–Jun 2026)
- **Goal**: Enable external clients to push traces and outcomes.
- **Deliverables**:
  - Public WebSocket / API for trace ingestion.
  - Event streaming (Kafka) for real-time analytics.
  - External provider integrations (e.g. Salesforce, Zendesk) for outcomes.
  - Granic (optional, self-hosted) for compliance-sensitive data residency.

## Phase 3: Multi-Industry Templates (Jul–Sep 2026)
- **Goal**: Adapt AgentLoop for use cases beyond support (e.g., sales, dev-tools, legal).
- **Deliverables**:
  - Outcome schema templates per industry.
  - Pre-built dashboard templates (React components).
  - Community marketplace for trace and outcome definitions.

## Phase 4: Agent Optimization (Oct–Dec 2026)
- **Goal**: Close the loop: auto-suggest A/B experiments for prompts, agent versions, and workflows.
- **Deliverables**:
  - A/B test harness (randomized user-slice routing).
  - Auto-root-cause: AI-generated summary of failure clusters.
  - Auto-recommend: experiments with the highest expected outcome lift.
  - Integration with CI to auto-deploy winning experiments with guardrails.

## Key Metrics (Success)
- **Accuracy**: >90% NLP classification on support feedback.
- **Latency**: Dashboard loads < 1s for 100k sessions.
- **Coverage**: 100% of synthetic traces attributed with outcomes.
- **Decision Support**: Lower time-to-insight by 5x vs manual log analysis.

## Answers the Key Questions
- **Which agent version performs best?** Outcome tracking shows per-version CSAT / resolution / conversion.
- **Which workflow path converts?** Workflow analytics.
- **Why do sessions fail?** Root cause insights + trace clustering.
- **What to fix next?** Insights surface highest-impact improvement candidates.
