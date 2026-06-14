# AgentLoop

![Build Status](https://github.com/sam1064max/agentloop/actions/workflows/ci.yml/badge.svg)
![Release](https://img.shields.io/github/v/release/sam1064max/agentloop)
![License](https://img.shields.io/github/license/sam1064max/agentloop)
![Coverage](https://img.shields.io/codecov/c/github/sam1064max/agentloop)

**AI Agent Analytics & Insights Platform**

AgentLoop provides comprehensive observability and analytics for AI agent systems. Track workflow execution, understand agent behavior patterns, and derive actionable insights to optimize agent performance.

---

## Architecture

```mermaid
graph TB
    subgraph Client
        FE[Frontend Dashboard]
    end

    subgraph Infrastructure
        GW[Gateway/Load Balancer]
        PM[Prometheus]
        GF[Grafana]
    end

    subgraph Core Services
        API[FastAPI Service<br/>:8000]
        ANALYTICS[Analytics Service<br/>:8001]
    end

    subgraph Data
        PG[(PostgreSQL<br/>Traces/Feedback<br/>Outcomes)]
        DUCK[(DuckDB<br/>Analytics<br/>Aggregations)]
    end

    FE --> GW
    GW --> API
    API --> PG
    API --> ANALYTICS
    ANALYTICS --> DUCK
    PM --> API
    PM --> ANALYTICS
    GF --> PM
```

## Quick Start

```bash
# Clone repository
git clone https://github.com/sam1064max/agentloop.git
cd agentloop

# Start all services
docker compose up -d

# Access dashboard
open http://localhost:8080
```

## Feature Matrix

| Feature | Status | Description |
|---------|--------|-------------|
| **Trace Ingestion** | ✅ Stable | Ingest agent execution traces via REST API |
| **Feedback Collection** | ✅ Stable | Collect human/automated feedback on agent outputs |
| **Outcome Tracking** | ✅ Stable | Track final outcomes and success metrics |
| **Workflow Analysis** | ✅ Stable | Analyze workflow paths and execution patterns |
| **Agent Version Comparison** | ✅ Stable | Compare performance across agent versions |
| **Root Cause Insights** | ✅ Stable | ML-powered root cause analysis |
| **Executive Dashboard** | ✅ Stable | KPI overview and executive reporting |
| **Custom Dashboards** | 🏗 WIP | Grafana dashboard builder |
| **Alerting** | 🏗 WIP | Anomaly detection and alerting |
| **Multi-Agent Support** | 🔮 Planned | Cross-agent correlation and analysis |

## Use Cases

### For AI Engineering Teams
- **Debug agent failures**: Trace execution paths reveal where and why agents fail
- **Optimize token usage**: Identify redundant calls and optimize prompts
- **A/B test agent versions**: Compare success rates across versions

### For Product Managers
- **Understand user journeys**: See how users interact with AI features
- **Track KPIs**: Monitor completion rates, satisfaction scores
- **Inform roadmap**: Data-driven decisions on agent improvements

### For Data Scientists
- **Feature engineering**: Use trace data for model improvement
- **Anomaly detection**: Identify unusual patterns in agent behavior
- **Attribution modeling**: Understand what drives positive outcomes

## Competitive Positioning

| Capability | AgentLoop | DataDog | Honeycomb | Custom |
|------------|-----------|---------|-----------|--------|
| Agent-specific metrics | ✅ | ❌ | ❌ | ❌ |
| Workflow path analysis | ✅ | ❌ | ❌ | ❌ |
| Agent version comparison | ✅ | ❌ | ❌ | ❌ |
| Root cause insights | ✅ | ❌ | 🟡 | ❌ |
| Outcome attribution | ✅ | ❌ | ❌ | ❌ |
| Fast setup (< 1 hour) | ✅ | ❌ | ❌ | ❌ |
| Open source | ✅ | ❌ | ❌ | N/A |

## Roadmap

```mermaid
gantt
    title AgentLoop Roadmap
    dateFormat  YYYY-MM
    section v1.x
    Multi-agent correlation    :2026-04, 2026-06
    Real-time alerting          :2026-04, 2026-07
    Custom dashboard builder    :2026-05, 2026-08
    section v2.0
    LLM-powered insights        :2026-07, 2026-09
    Automated optimization      :2026-08, 2026-10
    Enterprise features         :2026-09, 2026-12
```

## Screenshots

| Dashboard | Workflow Analysis |
|-----------|-------------------|
| ![Dashboard](docs/assets/dashboard-placeholder.png) | ![Workflow](docs/assets/workflow-placeholder.png) |

---

## License

MIT License - see [LICENSE](LICENSE) for details.