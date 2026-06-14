# AgentLoop API Documentation

## Base URL

```
Production: https://api.agentloop.dev/v1
Local:      http://localhost:8000/v1
```

## Authentication

All API requests require an API key in the header:

```
Authorization: Bearer <your-api-key>
```

## Rate Limits

| Tier | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Free | 100 | 10,000 |
| Pro | 1,000 | 100,000 |
| Enterprise | Unlimited | Unlimited |

## Common Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid API key |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Traces API

### Ingest Trace

Record an execution trace from an agent.

**POST** `/traces`

**Request Body:**
```json
{
  "session_id": "sess_abc123",
  "agent_id": "agent_gpt4_v2",
  "agent_version": "2.1.0",
  "trace_id": "trace_xyz789",
  "parent_span_id": null,
  "span_id": "span_def456",
  "operation_name": "user_intent_classification",
  "start_time": "2026-03-15T10:30:00Z",
  "end_time": "2026-03-15T10:30:00.150Z",
  "duration_ms": 150,
  "input_tokens": 120,
  "output_tokens": 45,
  "model": "gpt-4-turbo",
  "status": "success",
  "error_message": null,
  "metadata": {
    "intent": "bill inquiry",
    "confidence": 0.94
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "trace_123",
  "trace_id": "trace_xyz789",
  "status": "accepted"
}
```

### Get Trace

**GET** `/traces/{trace_id}`

**Response:** `200 OK`
```json
{
  "id": "trace_123",
  "trace_id": "trace_xyz789",
  "session_id": "sess_abc123",
  "agent_id": "agent_gpt4_v2",
  "operation_name": "user_intent_classification",
  "start_time": "2026-03-15T10:30:00Z",
  "end_time": "2026-03-15T10:30:00.150Z",
  "duration_ms": 150,
  "status": "success",
  "metadata": {
    "intent": "bill inquiry",
    "confidence": 0.94
  }
}
```

### List Traces

**GET** `/traces`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| session_id | string | - | Filter by session |
| agent_id | string | - | Filter by agent |
| start_date | ISO8601 | - | Start of date range |
| end_date | ISO8601 | - | End of date range |
| status | string | - | Filter by status (success/error) |
| limit | int | 100 | Max results (max 1000) |
| offset | int | 0 | Pagination offset |

---

## Feedback API

### Submit Feedback

**POST** `/feedback`

**Request Body:**
```json
{
  "trace_id": "trace_xyz789",
  "feedback_type": "human_rating",
  "score": 4,
  "category": "accuracy",
  "comment": "Correctly identified billing intent",
  "feedback_source": "human_evaluator",
  "metadata": {
    "evaluator_id": "eval_123",
    "evaluation_time_ms": 2500
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "fb_456",
  "trace_id": "trace_xyz789",
  "status": "accepted"
}
```

### Batch Submit Feedback

**POST** `/feedback/batch`

**Request Body:**
```json
{
  "feedback": [
    {
      "trace_id": "trace_001",
      "feedback_type": "human_rating",
      "score": 5,
      "category": "accuracy"
    },
    {
      "trace_id": "trace_002",
      "feedback_type": "human_rating",
      "score": 3,
      "category": "helpfulness"
    }
  ]
}
```

### Get Feedback for Trace

**GET** `/traces/{trace_id}/feedback`

**Response:** `200 OK`
```json
{
  "trace_id": "trace_xyz789",
  "feedback": [
    {
      "id": "fb_456",
      "feedback_type": "human_rating",
      "score": 4,
      "category": "accuracy",
      "comment": "Correctly identified billing intent",
      "created_at": "2026-03-15T11:00:00Z"
    }
  ]
}
```

---

## Outcomes API

### Record Outcome

**POST** `/outcomes`

**Request Body:**
```json
{
  "session_id": "sess_abc123",
  "agent_id": "agent_gpt4_v2",
  "outcome_type": "resolution",
  "outcome_value": "success",
  "resolution_time_ms": 45000,
  "user_satisfaction_score": 4.5,
  "task_completed": true,
  "escalation": false,
  "metadata": {
    "conversation_turns": 5,
    "user_region": "US-WEST"
  },
  "timestamp": "2026-03-15T10:35:00Z"
}
```

**Response:** `201 Created`
```json
{
  "id": "out_789",
  "session_id": "sess_abc123",
  "status": "accepted"
}
```

### Get Session Outcome

**GET** `/sessions/{session_id}/outcome`

**Response:** `200 OK`
```json
{
  "session_id": "sess_abc123",
  "outcome_type": "resolution",
  "outcome_value": "success",
  "resolution_time_ms": 45000,
  "user_satisfaction_score": 4.5,
  "task_completed": true,
  "created_at": "2026-03-15T10:35:00Z"
}
```

---

## Analytics API

### Get Session Analytics

**GET** `/analytics/sessions/{session_id}`

**Response:** `200 OK`
```json
{
  "session_id": "sess_abc123",
  "total_duration_ms": 45000,
  "trace_count": 12,
  "error_count": 1,
  "feedback_scores": [4, 5, 4, 5],
  "avg_feedback_score": 4.5,
  "workflow_path": [
    "intent_classification",
    "entity_extraction",
    "policy_lookup",
    "response_generation"
  ]
}
```

### Get Agent Performance

**GET** `/analytics/agents/{agent_id}/performance`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | ISO8601 | Start of period |
| end_date | ISO8601 | End of period |
| version | string | Filter by version |

**Response:** `200 OK`
```json
{
  "agent_id": "agent_gpt4_v2",
  "period": {
    "start": "2026-03-01",
    "end": "2026-03-15"
  },
  "metrics": {
    "total_traces": 45230,
    "success_rate": 0.942,
    "avg_duration_ms": 230,
    "p50_duration_ms": 180,
    "p95_duration_ms": 450,
    "p99_duration_ms": 890,
    "avg_tokens_per_call": 285,
    "error_rate": 0.058,
    "avg_feedback_score": 4.2
  },
  "by_version": [
    {"version": "2.1.0", "success_rate": 0.95},
    {"version": "2.0.0", "success_rate": 0.91}
  ]
}
```

### Get Workflow Analysis

**GET** `/analytics/workflows/{workflow_name}/analysis`

**Response:** `200 OK`
```json
{
  "workflow_name": "customer_support",
  "total_executions": 15420,
  "success_rate": 0.89,
  "avg_duration_ms": 32000,
  "path_distribution": [
    {"path": "intent→entity→policy→response", "count": 12000, "rate": 0.78},
    {"path": "intent→entity→clarification→response", "count": 2500, "rate": 0.16},
    {"path": "intent→escalation", "count": 920, "rate": 0.06}
  ],
  "bottlenecks": [
    {"operation": "policy_lookup", "avg_duration_ms": 8500, "impact": "high"}
  ]
}
```

### Get Root Cause Insights

**GET** `/analytics/insights`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| metric | string | Target metric (success_rate, latency) |
| threshold | float | Deviation threshold (default 0.1) |
| limit | int | Max insights (default 10) |

**Response:** `200 OK`
```json
{
  "insights": [
    {
      "id": "ins_001",
      "metric": "success_rate",
      "severity": "high",
      "description": "Policy lookup errors increased 23% for version 2.0.x",
      "root_cause": "Policy service timeout threshold too aggressive",
      "recommendation": "Increase timeout from 2s to 5s for policy service calls",
      "affected_traces": 892,
      "estimated_impact": "+2.1% success rate",
      "created_at": "2026-03-15T08:00:00Z"
    }
  ]
}
```

### Compare Agent Versions

**POST** `/analytics/compare`

**Request Body:**
```json
{
  "agent_id": "agent_gpt4_v2",
  "versions": ["2.0.0", "2.1.0"],
  "metrics": ["success_rate", "avg_duration_ms", "avg_feedback_score"]
}
```

**Response:** `200 OK`
```json
{
  "agent_id": "agent_gpt4_v2",
  "comparison": {
    "success_rate": {
      "2.0.0": 0.91,
      "2.1.0": 0.95,
      "delta": 0.04,
      "significant": true
    },
    "avg_duration_ms": {
      "2.0.0": 250,
      "2.1.0": 230,
      "delta": -20,
      "significant": true
    },
    "avg_feedback_score": {
      "2.0.0": 4.0,
      "2.1.0": 4.2,
      "delta": 0.2,
      "significant": false
    }
  }
}
```

---

## Sessions API

### Get Session Details

**GET** `/sessions/{session_id}`

**Response:** `200 OK`
```json
{
  "session_id": "sess_abc123",
  "agent_id": "agent_gpt4_v2",
  "agent_version": "2.1.0",
  "started_at": "2026-03-15T10:30:00Z",
  "ended_at": "2026-03-15T10:35:00Z",
  "status": "completed",
  "outcome": "success",
  "trace_count": 12,
  "metadata": {
    "user_id": "user_456",
    "channel": "web"
  }
}
```

### List Sessions

**GET** `/sessions`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| agent_id | string | - | Filter by agent |
| start_date | ISO8601 | - | Start of date range |
| end_date | ISO8601 | - | End of date range |
| status | string | - | Filter by status |
| limit | int | 100 | Max results |
| offset | int | 0 | Pagination offset |

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 1001 | INVALID_TRACE_DATA | Trace data validation failed |
| 1002 | DUPLICATE_TRACE | Trace ID already exists |
| 2001 | INVALID_FEEDBACK_DATA | Feedback validation failed |
| 2002 | TRACE_NOT_FOUND | Referenced trace does not exist |
| 3001 | INVALID_OUTCOME_DATA | Outcome validation failed |
| 4001 | ANALYTICS_ERROR | Analytics query failed |
| 5001 | INTERNAL_ERROR | Unexpected server error |

---

## SDK Examples

### Python

```python
from agentloop import AgentLoopClient

client = AgentLoopClient(api_key="your-api-key")

# Record a trace
client.trace.create(
    session_id="sess_123",
    agent_id="my_agent",
    operation_name="classify_intent",
    duration_ms=150,
    status="success"
)

# Submit feedback
client.feedback.submit(
    trace_id="trace_456",
    score=5,
    category="accuracy"
)
```

### JavaScript/TypeScript

```typescript
import { AgentLoopClient } from '@agentloop/sdk';

const client = new AgentLoopClient({ apiKey: 'your-api-key' });

// Record a trace
await client.traces.create({
  sessionId: 'sess_123',
  agentId: 'my_agent',
  operationName: 'classify_intent',
  durationMs: 150,
  status: 'success'
});
```