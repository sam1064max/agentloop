import axios, { AxiosInstance } from 'axios';
import type {
  Session,
  Trace,
  Feedback,
  Outcome,
  AnalyticsData,
  PathAnalysis,
  AgentComparison,
  Recommendation,
  PaginatedResponse,
  RootCauseInsight,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const generateId = () => Math.random().toString(36).substring(2, 15);

const sampleTraces: Trace[] = [
  {
    id: 'trace-001',
    sessionId: 'sess-001',
    agentVersion: 'v2.3.1',
    toolCalls: [
      { id: 'tc-001', name: 'searchDatabase', arguments: { query: 'user_preferences' }, result: { found: 42 }, duration: 145, timestamp: '2026-06-14T10:00:00Z', success: true },
      { id: 'tc-002', name: 'processData', arguments: { records: 42 }, result: { processed: 42 }, duration: 320, timestamp: '2026-06-14T10:00:15Z', success: true },
      { id: 'tc-003', name: 'generateResponse', arguments: { format: 'json' }, duration: 89, timestamp: '2026-06-14T10:00:20Z', success: true },
    ],
    startTime: '2026-06-14T10:00:00Z',
    endTime: '2026-06-14T10:00:25Z',
    status: 'completed',
  },
  {
    id: 'trace-002',
    sessionId: 'sess-002',
    agentVersion: 'v2.3.1',
    toolCalls: [
      { id: 'tc-004', name: 'searchDatabase', arguments: { query: 'orders' }, result: { found: 156 }, duration: 234, timestamp: '2026-06-14T10:05:00Z', success: true },
      { id: 'tc-005', name: 'validateInput', arguments: { schema: 'order' }, duration: 45, timestamp: '2026-06-14T10:05:05Z', success: true },
      { id: 'tc-006', name: 'processData', arguments: { records: 156 }, duration: 567, timestamp: '2026-06-14T10:05:10Z', success: true },
    ],
    startTime: '2026-06-14T10:05:00Z',
    endTime: '2026-06-14T10:05:20Z',
    status: 'completed',
  },
  {
    id: 'trace-003',
    sessionId: 'sess-003',
    agentVersion: 'v2.4.0',
    toolCalls: [
      { id: 'tc-007', name: 'searchDatabase', arguments: { query: 'inventory' }, result: { found: 89 }, duration: 189, timestamp: '2026-06-14T10:10:00Z', success: true },
      { id: 'tc-008', name: 'calculateMetrics', arguments: { type: 'inventory' }, duration: 123, timestamp: '2026-06-14T10:10:05Z', success: true },
    ],
    startTime: '2026-06-14T10:10:00Z',
    endTime: '2026-06-14T10:10:15Z',
    status: 'completed',
  },
  {
    id: 'trace-004',
    sessionId: 'sess-004',
    agentVersion: 'v2.3.1',
    toolCalls: [
      { id: 'tc-009', name: 'fetchUser', arguments: { id: 'user-123' }, duration: 78, timestamp: '2026-06-14T10:15:00Z', success: true },
      { id: 'tc-010', name: 'updatePreferences', arguments: { theme: 'dark' }, error: 'Connection timeout', duration: 5000, timestamp: '2026-06-14T10:15:05Z', success: false, error: 'Connection timeout' },
    ],
    startTime: '2026-06-14T10:15:00Z',
    status: 'failed',
  },
];

const sampleSessions: Session[] = [
  {
    id: 'sess-001',
    userId: 'user-1001',
    agentVersion: 'v2.3.1',
    startTime: '2026-06-14T10:00:00Z',
    endTime: '2026-06-14T10:00:25Z',
    status: 'completed',
    traces: [sampleTraces[0]],
    feedback: [{ id: 'fb-001', sessionId: 'sess-001', type: 'thumbs_up', score: 5, timestamp: '2026-06-14T10:01:00Z', agentVersion: 'v2.3.1' }],
    outcomes: [{ id: 'out-001', sessionId: 'sess-001', traceId: 'trace-001', type: 'success', value: 150, timestamp: '2026-06-14T10:01:00Z' }],
  },
  {
    id: 'sess-002',
    userId: 'user-1002',
    agentVersion: 'v2.3.1',
    startTime: '2026-06-14T10:05:00Z',
    endTime: '2026-06-14T10:05:20Z',
    status: 'completed',
    traces: [sampleTraces[1]],
    feedback: [{ id: 'fb-002', sessionId: 'sess-002', type: 'thumbs_up', score: 4, timestamp: '2026-06-14T10:06:00Z', agentVersion: 'v2.3.1' }],
    outcomes: [{ id: 'out-002', sessionId: 'sess-002', traceId: 'trace-002', type: 'success', value: 320, timestamp: '2026-06-14T10:06:00Z' }],
  },
  {
    id: 'sess-003',
    userId: 'user-1003',
    agentVersion: 'v2.4.0',
    startTime: '2026-06-14T10:10:00Z',
    endTime: '2026-06-14T10:10:15Z',
    status: 'completed',
    traces: [sampleTraces[2]],
    feedback: [{ id: 'fb-003', sessionId: 'sess-003', type: 'thumbs_up', score: 5, timestamp: '2026-06-14T10:11:00Z', agentVersion: 'v2.4.0' }],
    outcomes: [{ id: 'out-003', sessionId: 'sess-003', traceId: 'trace-003', type: 'success', value: 89, timestamp: '2026-06-14T10:11:00Z' }],
  },
  {
    id: 'sess-004',
    userId: 'user-1004',
    agentVersion: 'v2.3.1',
    startTime: '2026-06-14T10:15:00Z',
    status: 'failed',
    traces: [sampleTraces[3]],
    feedback: [{ id: 'fb-004', sessionId: 'sess-004', type: 'escalation', comment: 'User had to retry manually', timestamp: '2026-06-14T10:16:00Z', agentVersion: 'v2.3.1' }],
    outcomes: [{ id: 'out-004', sessionId: 'sess-004', traceId: 'trace-004', type: 'failure', value: -50, timestamp: '2026-06-14T10:16:00Z' }],
  },
];

const sampleFeedback: Feedback[] = [
  { id: 'fb-001', sessionId: 'sess-001', type: 'thumbs_up', score: 5, timestamp: '2026-06-14T10:01:00Z', agentVersion: 'v2.3.1' },
  { id: 'fb-002', sessionId: 'sess-002', type: 'thumbs_up', score: 4, timestamp: '2026-06-14T10:06:00Z', agentVersion: 'v2.3.1' },
  { id: 'fb-003', sessionId: 'sess-003', type: 'thumbs_up', score: 5, timestamp: '2026-06-14T10:11:00Z', agentVersion: 'v2.4.0' },
  { id: 'fb-004', sessionId: 'sess-004', type: 'escalation', comment: 'Connection issues', timestamp: '2026-06-14T10:16:00Z', agentVersion: 'v2.3.1' },
  { id: 'fb-005', sessionId: 'sess-005', type: 'thumbs_down', score: 2, comment: 'Slow response', timestamp: '2026-06-14T09:30:00Z', agentVersion: 'v2.3.0' },
];

const sampleOutcomes: Outcome[] = [
  { id: 'out-001', sessionId: 'sess-001', type: 'success', value: 150, timestamp: '2026-06-14T10:01:00Z' },
  { id: 'out-002', sessionId: 'sess-002', type: 'success', value: 320, timestamp: '2026-06-14T10:06:00Z' },
  { id: 'out-003', sessionId: 'sess-003', type: 'success', value: 89, timestamp: '2026-06-14T10:11:00Z' },
  { id: 'out-004', sessionId: 'sess-004', type: 'failure', value: -50, timestamp: '2026-06-14T10:16:00Z' },
];

const sampleAnalytics: AnalyticsData = {
  sessionsCount: 1247,
  sessionsTrend: 12.5,
  successRate: 94.2,
  successRateTrend: 2.3,
  escalationRate: 3.8,
  escalationRateTrend: -1.2,
  csat: 4.6,
  csatTrend: 0.3,
  sessionsOverTime: [
    { timestamp: '2026-06-07', value: 1024, label: 'Week 23' },
    { timestamp: '2026-06-08', value: 1156, label: 'Week 24' },
    { timestamp: '2026-06-09', value: 1089, label: 'Week 25' },
    { timestamp: '2026-06-10', value: 1234, label: 'Week 26' },
    { timestamp: '2026-06-11', value: 1198, label: 'Week 27' },
    { timestamp: '2026-06-12', value: 1342, label: 'Week 28' },
    { timestamp: '2026-06-13', value: 1247, label: 'Week 29' },
  ],
  successRateOverTime: [
    { timestamp: '2026-06-07', value: 91.2 },
    { timestamp: '2026-06-08', value: 92.8 },
    { timestamp: '2026-06-09', value: 93.1 },
    { timestamp: '2026-06-10', value: 92.5 },
    { timestamp: '2026-06-11', value: 93.8 },
    { timestamp: '2026-06-12', value: 94.5 },
    { timestamp: '2026-06-13', value: 94.2 },
  ],
  outcomesByType: [
    { name: 'Success', value: 1175, color: '#22c55e' },
    { name: 'Failure', value: 42, color: '#ef4444' },
    { name: 'Escalation', value: 30, color: '#f59e0b' },
  ],
  toolUsageByAgent: [
    { name: 'searchDatabase', count: 892, avgDuration: 156 },
    { name: 'processData', count: 756, avgDuration: 312 },
    { name: 'generateResponse', count: 1247, avgDuration: 87 },
    { name: 'validateInput', count: 423, avgDuration: 45 },
    { name: 'calculateMetrics', count: 234, avgDuration: 112 },
  ],
};

const sampleAgentComparisons: AgentComparison[] = [
  { version: 'v2.4.0', sessionsCount: 342, successRate: 96.8, avgDuration: 1240, avgOutcomeValue: 187, feedbackScore: 4.7, escalationRate: 2.1, trend: 'up' },
  { version: 'v2.3.1', sessionsCount: 489, successRate: 94.2, avgDuration: 1456, avgOutcomeValue: 156, feedbackScore: 4.5, escalationRate: 3.8, trend: 'stable' },
  { version: 'v2.3.0', sessionsCount: 267, successRate: 91.5, avgDuration: 1623, avgOutcomeValue: 134, feedbackScore: 4.2, escalationRate: 5.9, trend: 'down' },
  { version: 'v2.2.5', sessionsCount: 149, successRate: 88.9, avgDuration: 1890, avgOutcomeValue: 112, feedbackScore: 3.9, escalationRate: 8.2, trend: 'down' },
];

const samplePathAnalysis: PathAnalysis = {
  nodes: [
    { id: 'start', name: 'User Request', count: 1247, successRate: 100, avgDuration: 0 },
    { id: 'auth', name: 'Authentication', count: 1247, successRate: 99.8, avgDuration: 45 },
    { id: 'search', name: 'Search Database', count: 1156, successRate: 98.5, avgDuration: 156 },
    { id: 'process', name: 'Process Data', count: 1089, successRate: 96.2, avgDuration: 312 },
    { id: 'validate', name: 'Validate Input', count: 423, successRate: 94.8, avgDuration: 45 },
    { id: 'calculate', name: 'Calculate Metrics', count: 234, successRate: 97.4, avgDuration: 112 },
    { id: 'respond', name: 'Generate Response', count: 1198, successRate: 99.1, avgDuration: 87 },
    { id: 'end-success', name: 'Completed', count: 1175, successRate: 100, avgDuration: 0 },
    { id: 'end-failure', name: 'Failed', count: 42, successRate: 0, avgDuration: 0 },
    { id: 'end-escalation', name: 'Escalated', count: 30, successRate: 0, avgDuration: 0 },
  ],
  edges: [
    { source: 'start', target: 'auth', count: 1247, successRate: 99.8 },
    { source: 'auth', target: 'search', count: 1245, successRate: 98.5 },
    { source: 'search', target: 'process', count: 1098, successRate: 96.2 },
    { source: 'search', target: 'validate', count: 145, successRate: 94.8 },
    { source: 'search', target: 'calculate', count: 234, successRate: 97.4 },
    { source: 'process', target: 'respond', count: 1056, successRate: 99.1 },
    { source: 'validate', target: 'respond', count: 137, successRate: 98.5 },
    { source: 'calculate', target: 'respond', count: 228, successRate: 99.1 },
    { source: 'respond', target: 'end-success', count: 1175, successRate: 100 },
    { source: 'process', target: 'end-failure', count: 23, successRate: 0 },
    { source: 'validate', target: 'end-escalation', count: 6, successRate: 0 },
    { source: 'calculate', target: 'end-escalation', count: 3, successRate: 0 },
  ],
  totalSessions: 1247,
  avgPathLength: 4.2,
  mostCommonPath: ['User Request', 'Authentication', 'Search Database', 'Process Data', 'Generate Response', 'Completed'],
};

const sampleRecommendations: Recommendation[] = [
  {
    id: 'rec-001',
    category: 'performance',
    title: 'Optimize searchDatabase queries',
    description: 'Add index on frequently queried columns to reduce average query time by 40%. Current avg duration of 156ms can be reduced to under 100ms.',
    impact: 'high',
    impactScore: 87,
    effort: 'medium',
    agentVersions: ['v2.3.1', 'v2.3.0'],
    createdAt: '2026-06-13T15:00:00Z',
    status: 'pending',
  },
  {
    id: 'rec-002',
    category: 'quality',
    title: 'Implement retry logic for network timeouts',
    description: 'Connection timeouts cause 60% of failures. Implement exponential backoff retry mechanism with 3 attempts.',
    impact: 'high',
    impactScore: 82,
    effort: 'low',
    agentVersions: ['v2.3.1', 'v2.3.0', 'v2.2.5'],
    createdAt: '2026-06-12T10:00:00Z',
    status: 'accepted',
  },
  {
    id: 'rec-003',
    category: 'reliability',
    title: 'Upgrade to v2.4.0 across all agents',
    description: 'v2.4.0 shows 96.8% success rate vs 94.2% in v2.3.1. Upgrade recommended to reduce escalation rate by 45%.',
    impact: 'high',
    impactScore: 91,
    effort: 'low',
    agentVersions: ['v2.3.1', 'v2.3.0'],
    createdAt: '2026-06-11T08:00:00Z',
    status: 'pending',
  },
  {
    id: 'rec-004',
    category: 'cost',
    title: 'Batch processData operations',
    description: 'Current implementation processes records individually. Batching could reduce total processing time by 30% and cost by 25%.',
    impact: 'medium',
    impactScore: 68,
    effort: 'high',
    agentVersions: ['v2.3.1'],
    createdAt: '2026-06-10T14:00:00Z',
    status: 'rejected',
  },
  {
    id: 'rec-005',
    category: 'optimization',
    title: 'Cache validated inputs',
    description: 'Repeated validations on same inputs consume 12% of compute time. Implement LRU cache with 5-minute TTL.',
    impact: 'medium',
    impactScore: 55,
    effort: 'medium',
    agentVersions: ['v2.4.0', 'v2.3.1'],
    createdAt: '2026-06-09T09:00:00Z',
    status: 'implemented',
  },
];

const sampleInsights: RootCauseInsight[] = [
  {
    id: 'insight-001',
    type: 'bottleneck',
    title: 'processData latency spike after 1000 records',
    description: 'Processing time increases non-linearly when handling more than 1000 records. Memory allocation appears suboptimal.',
    affectedTraces: 156,
    impactScore: 78,
    recommendation: 'Implement chunked processing for large datasets',
    confidence: 0.89,
    timestamp: '2026-06-13T12:00:00Z',
  },
  {
    id: 'insight-002',
    type: 'error',
    title: 'Database connection pool exhaustion',
    description: 'Peak hours show connection timeout errors due to pool limits. Average wait time exceeds 2 seconds.',
    affectedTraces: 89,
    impactScore: 85,
    recommendation: 'Increase pool size from 10 to 25 connections',
    confidence: 0.94,
    timestamp: '2026-06-12T18:00:00Z',
  },
  {
    id: 'insight-003',
    type: 'pattern',
    title: '特定用户群体的高失败率',
    description: 'Enterprise tier users show 15% lower success rate compared to other tiers during business hours.',
    affectedTraces: 67,
    impactScore: 72,
    recommendation: 'Investigate enterprise-specific configurations and rate limits',
    confidence: 0.81,
    timestamp: '2026-06-11T09:00:00Z',
  },
];

export async function fetchAnalytics(): Promise<AnalyticsData> {
  try {
    const response = await apiClient.get<AnalyticsData>('/analytics');
    return response.data;
  } catch {
    return sampleAnalytics;
  }
}

export async function fetchSessions(page = 1, pageSize = 20): Promise<PaginatedResponse<Session>> {
  try {
    const response = await apiClient.get<PaginatedResponse<Session>>('/sessions', {
      params: { page, pageSize },
    });
    return response.data;
  } catch {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return {
      data: sampleSessions.slice(start, end),
      total: sampleSessions.length,
      page,
      pageSize,
      hasMore: end < sampleSessions.length,
    };
  }
}

export async function fetchSession(id: string): Promise<Session | null> {
  try {
    const response = await apiClient.get<Session>(`/sessions/${id}`);
    return response.data;
  } catch {
    return sampleSessions.find((s) => s.id === id) || null;
  }
}

export async function fetchTraces(sessionId?: string): Promise<Trace[]> {
  try {
    const response = await apiClient.get<Trace[]>('/traces', {
      params: sessionId ? { sessionId } : undefined,
    });
    return response.data;
  } catch {
    if (sessionId) {
      return sampleTraces.filter((t) => t.sessionId === sessionId);
    }
    return sampleTraces;
  }
}

export async function fetchTrace(id: string): Promise<Trace | null> {
  try {
    const response = await apiClient.get<Trace>(`/traces/${id}`);
    return response.data;
  } catch {
    return sampleTraces.find((t) => t.id === id) || null;
  }
}

export async function fetchFeedback(): Promise<Feedback[]> {
  try {
    const response = await apiClient.get<Feedback[]>('/feedback');
    return response.data;
  } catch {
    return sampleFeedback;
  }
}

export async function fetchOutcomes(): Promise<Outcome[]> {
  try {
    const response = await apiClient.get<Outcome[]>('/outcomes');
    return response.data;
  } catch {
    return sampleOutcomes;
  }
}

export async function fetchAgentComparisons(): Promise<AgentComparison[]> {
  try {
    const response = await apiClient.get<AgentComparison[]>('/agents/comparisons');
    return response.data;
  } catch {
    return sampleAgentComparisons;
  }
}

export async function fetchPathAnalysis(): Promise<PathAnalysis> {
  try {
    const response = await apiClient.get<PathAnalysis>('/analysis/paths');
    return response.data;
  } catch {
    return samplePathAnalysis;
  }
}

export async function fetchRecommendations(): Promise<Recommendation[]> {
  try {
    const response = await apiClient.get<Recommendation[]>('/recommendations');
    return response.data;
  } catch {
    return sampleRecommendations;
  }
}

export async function fetchInsights(): Promise<RootCauseInsight[]> {
  try {
    const response = await apiClient.get<RootCauseInsight[]>('/insights');
    return response.data;
  } catch {
    return sampleInsights;
  }
}

export async function ingestTrace(trace: Omit<Trace, 'id'>): Promise<Trace> {
  try {
    const response = await apiClient.post<Trace>('/ingest/traces', trace);
    return response.data;
  } catch {
    const newTrace: Trace = { ...trace, id: `trace-${generateId()}` };
    sampleTraces.push(newTrace);
    return newTrace;
  }
}

export async function ingestFeedback(feedback: Omit<Feedback, 'id'>): Promise<Feedback> {
  try {
    const response = await apiClient.post<Feedback>('/ingest/feedback', feedback);
    return response.data;
  } catch {
    const newFeedback: Feedback = { ...feedback, id: `fb-${generateId()}` };
    sampleFeedback.push(newFeedback);
    return newFeedback;
  }
}

export async function ingestOutcome(outcome: Omit<Outcome, 'id'>): Promise<Outcome> {
  try {
    const response = await apiClient.post<Outcome>('/ingest/outcomes', outcome);
    return response.data;
  } catch {
    const newOutcome: Outcome = { ...outcome, id: `out-${generateId()}` };
    sampleOutcomes.push(newOutcome);
    return newOutcome;
  }
}

export const api = {
  fetchAnalytics,
  fetchSessions,
  fetchSession,
  fetchTraces,
  fetchTrace,
  fetchFeedback,
  fetchOutcomes,
  fetchAgentComparisons,
  fetchPathAnalysis,
  fetchRecommendations,
  fetchInsights,
  ingestTrace,
  ingestFeedback,
  ingestOutcome,
};

export default api;