export interface ToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
  result?: unknown;
  duration: number;
  timestamp: string;
  success: boolean;
  error?: string;
}

export interface Trace {
  id: string;
  sessionId: string;
  agentVersion: string;
  toolCalls: ToolCall[];
  startTime: string;
  endTime?: string;
  status: 'running' | 'completed' | 'failed';
  metadata?: Record<string, unknown>;
}

export interface Feedback {
  id: string;
  sessionId: string;
  traceId?: string;
  type: 'thumbs_up' | 'thumbs_down' | 'escalation' | 'correction';
  score?: number;
  comment?: string;
  timestamp: string;
  agentVersion: string;
}

export interface Outcome {
  id: string;
  sessionId: string;
  traceId?: string;
  type: 'success' | 'failure' | 'escalation';
  value: number;
  currency?: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface Session {
  id: string;
  userId?: string;
  agentVersion: string;
  startTime: string;
  endTime?: string;
  status: 'active' | 'completed' | 'failed';
  traces: Trace[];
  feedback?: Feedback[];
  outcomes?: Outcome[];
  metadata?: Record<string, unknown>;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface AnalyticsData {
  sessionsCount: number;
  sessionsTrend: number;
  successRate: number;
  successRateTrend: number;
  escalationRate: number;
  escalationRateTrend: number;
  csat: number;
  csatTrend: number;
  sessionsOverTime: TimeSeriesDataPoint[];
  successRateOverTime: TimeSeriesDataPoint[];
  outcomesByType: { name: string; value: number; color: string }[];
  toolUsageByAgent: { name: string; count: number; avgDuration: number }[];
}

export interface PathNode {
  id: string;
  name: string;
  count: number;
  successRate: number;
  avgDuration: number;
}

export interface PathEdge {
  source: string;
  target: string;
  count: number;
  successRate: number;
}

export interface PathAnalysis {
  nodes: PathNode[];
  edges: PathEdge[];
  totalSessions: number;
  avgPathLength: number;
  mostCommonPath: string[];
}

export interface AgentComparison {
  version: string;
  sessionsCount: number;
  successRate: number;
  avgDuration: number;
  avgOutcomeValue: number;
  feedbackScore: number;
  escalationRate: number;
  trend: 'up' | 'down' | 'stable';
}

export interface RootCauseInsight {
  id: string;
  type: 'error' | 'bottleneck' | 'pattern' | 'anomaly';
  title: string;
  description: string;
  affectedTraces: number;
  impactScore: number;
  recommendation: string;
  confidence: number;
  timestamp: string;
}

export interface Recommendation {
  id: string;
  category: 'optimization' | 'quality' | 'cost' | 'performance' | 'reliability';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  impactScore: number;
  effort: 'low' | 'medium' | 'high';
  agentVersions?: string[];
  createdAt: string;
  status: 'pending' | 'accepted' | 'rejected' | 'implemented';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, unknown>;
}