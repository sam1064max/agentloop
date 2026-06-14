# AgentLoop Architecture

## System Overview

AgentLoop is a distributed analytics platform designed for AI agent observability. The system ingests traces, feedback, and outcomes from agent systems and provides actionable insights through dashboards and APIs.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Client Applications                          │
│    (AI Agents, Human Feedback Systems, External Monitoring)         │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Service (:8000)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │  Traces  │  │ Feedback │  │ Outcomes │  │ Analytics Proxy  │   │
│  │  Endpoint│  │ Endpoint │  │ Endpoint │  │                  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
         │                │                │                │
         ▼                ▼                ▼                ▼
┌─────────────────┐                                   ┌─────────────────┐
│   PostgreSQL    │                                   │     DuckDB      │
│   (Primary)     │─────────── ETL ─────────────────▶│   (Analytics)   │
│                 │                                   │                 │
└─────────────────┘                                   └─────────────────┘
                                                              │
                                                              ▼
                                               ┌─────────────────────────┐
                                               │   Analytics Service      │
                                               │   (:8001)                │
                                               │   - Aggregation         │
                                               │   - Attribution         │
                                               │   - Insights            │
                                               └─────────────────────────┘
```

## Core Components

### 1. FastAPI Service (Backend API)

**Responsibilities:**
- RESTful API for data ingestion
- Authentication and authorization
- Request validation
- Data persistence to PostgreSQL
- Proxying analytics queries

**Technology:** Python, FastAPI, SQLAlchemy, Pydantic

**Key Endpoints:**
- `POST /api/v1/traces` - Ingest execution traces
- `POST /api/v1/feedback` - Submit feedback
- `POST /api/v1/outcomes` - Record outcomes
- `GET /api/v1/analytics/*` - Query analytics

### 2. Analytics Service

**Responsibilities:**
- Heavy analytical queries on DuckDB
- Pre-computed aggregations
- Attribution modeling
- ML-based insights generation

**Technology:** Python, FastAPI, DuckDB, Pandas

**Key Operations:**
- Workflow path analysis
- Agent version comparison
- Root cause attribution
- Anomaly detection

### 3. PostgreSQL Database

**Purpose:** Primary data store for operational data

**Schema:**
- `traces` - Execution traces with spans
- `feedback` - Feedback records linked to traces
- `outcomes` - Final outcomes with metrics
- `agents` - Agent metadata and versions
- `sessions` - Session tracking

### 4. DuckDB Database

**Purpose:** OLAP-style analytics on imported data

**Tables:**
- `analytics_sessions` - Denormalized session view
- `workflow_paths` - Aggregated path analysis
- `agent_metrics` - Per-agent performance metrics
- `insights` - Generated insights and recommendations

## Data Flow

### Ingestion Flow

```
1. Agent SDK → POST /traces → FastAPI → PostgreSQL
2. Agent SDK → POST /feedback → FastAPI → PostgreSQL
3. Agent SDK → POST /outcomes → FastAPI → PostgreSQL
```

### Analytics Flow

```
1. PostgreSQL → ETL Job → DuckDB (hourly sync)
2. Dashboard → GET /analytics/* → FastAPI → Analytics Service → DuckDB
3. Insights Engine → DuckDB → Root cause analysis → PostgreSQL (insights)
```

## Deployment Architecture

```
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │ HTTPS
                    ┌──────▼──────┐
                    │   Grafana   │
                    │   (:3000)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
        │  Frontend │ │   API   │ │Analytics  │
        │  (:8080)  │ │ (:8000) │ │ (:8001)   │
        └───────────┘ └────┬────┘ └─────┬─────┘
                           │            │
                    ┌──────▼────────────▼──────┐
                    │      PostgreSQL (:5432)   │
                    └───────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │    DuckDB   │
                    └─────────────┘
```

## Security

### Authentication
- API key-based authentication for agent SDK
- OAuth 2.0 for dashboard users (Grafana)

### Authorization
- Role-based access control (RBAC)
- API keys scoped to specific agent IDs

### Data Protection
- TLS in transit
- Encrypted volumes at rest
- PII handling per GDPR guidelines

## Scalability

### Horizontal Scaling
- API and Analytics services are stateless
- Add replicas behind load balancer
- PostgreSQL with read replicas (future)

### Vertical Scaling
- DuckDB scales with data size
- Partition PostgreSQL tables by time
- Archive old data to cold storage

## Observability

### Metrics (Prometheus)
- `agentloop_api_requests_total` - Request counter by endpoint
- `agentloop_api_latency_seconds` - Request latency histogram
- `agentloop_db_connections` - Database pool usage
- `agentloop_analytics_query_duration` - Query performance

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing

### Tracing
- OpenTelemetry instrumentation
- Span context propagation
- Export to Jaeger (optional)

## Disaster Recovery

### Backup Strategy
- PostgreSQL: Daily automated backups, 30-day retention
- DuckDB: Point-in-time recovery via PostgreSQL sync
- Configuration: GitOps with version control

### RTO/RPO
- RTO: 4 hours
- RPO: 1 hour