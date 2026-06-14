import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, ChevronRight, ChevronDown, Play, CheckCircle, XCircle, AlertTriangle, Clock } from 'lucide-react';
import { fetchSessions, fetchTraces, fetchSession } from '../services/api';
import type { Session, Trace, ToolCall } from '../types';
import clsx from 'clsx';

export default function TraceExplorer() {
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
  const [expandedTools, setExpandedTools] = useState<Set<string>>(new Set());

  const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => fetchSessions(1, 50),
  });

  const { data: traces } = useQuery({
    queryKey: ['traces', selectedSession?.id],
    queryFn: () => selectedSession ? fetchTraces(selectedSession.id) : Promise.resolve([]),
    enabled: !!selectedSession,
  });

  const handleSessionClick = async (session: Session) => {
    const fullSession = await fetchSession(session.id);
    setSelectedSession(fullSession);
    setSelectedTrace(null);
  };

  const handleTraceClick = (trace: Trace) => {
    setSelectedTrace(trace);
    setExpandedTools(new Set());
  };

  const toggleTool = (toolId: string) => {
    const newExpanded = new Set(expandedTools);
    if (newExpanded.has(toolId)) {
      newExpanded.delete(toolId);
    } else {
      newExpanded.add(toolId);
    }
    setExpandedTools(newExpanded);
  };

  const getStatusIcon = (status: Session['status'] | Trace['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-danger-500" />;
      case 'running':
        return <Play className="w-4 h-4 text-agentloop-500 animate-pulse" />;
      case 'active':
        return <Clock className="w-4 h-4 text-warning-500" />;
      default:
        return null;
    }
  };

  const formatDuration = (start: string, end?: string) => {
    if (!end) return 'Running...';
    const ms = new Date(end).getTime() - new Date(start).getTime();
    return `${ms}ms`;
  };

  if (sessionsLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="card h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Trace Explorer</h1>
        <p className="text-slate-500 mt-1">Search and analyze individual agent execution traces</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="card p-0">
            <div className="p-4 border-b border-slate-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search sessions..."
                  className="input w-full pl-10"
                />
              </div>
            </div>

            <div className="divide-y divide-slate-200 max-h-[600px] overflow-y-auto">
              {sessionsData?.data.map((session) => (
                <button
                  key={session.id}
                  onClick={() => handleSessionClick(session)}
                  className={clsx(
                    'w-full p-4 text-left hover:bg-slate-50 transition-colors',
                    selectedSession?.id === session.id && 'bg-agentloop-50 border-l-2 border-agentloop-500'
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(session.status)}
                        <span className="font-mono text-sm text-slate-900 truncate">
                          {session.id}
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-slate-500">
                        v{session.agentVersion} • {new Date(session.startTime).toLocaleString()}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-400 flex-shrink-0" />
                  </div>

                  {session.traces && session.traces.length > 0 && (
                    <div className="mt-2 flex items-center gap-2">
                      <span className="badge-info text-xs">
                        {session.traces.length} trace{session.traces.length !== 1 ? 's' : ''}
                      </span>
                      {session.feedback && session.feedback.length > 0 && (
                        <span className={clsx(
                          'badge text-xs',
                          session.feedback[0].type === 'thumbs_up' && 'bg-success-100 text-success-700',
                          session.feedback[0].type === 'thumbs_down' && 'bg-danger-100 text-danger-700',
                          session.feedback[0].type === 'escalation' && 'bg-warning-100 text-warning-700'
                        )}>
                          {session.feedback[0].type.replace('_', ' ')}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2">
          {!selectedSession ? (
            <div className="card flex items-center justify-center h-96 text-slate-500">
              <div className="text-center">
                <Search className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p>Select a session to view traces</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">Session {selectedSession.id}</h2>
                    <div className="mt-1 flex items-center gap-4 text-sm text-slate-500">
                      <span>Version: <span className="font-mono text-agentloop-600">{selectedSession.agentVersion}</span></span>
                      <span>Status: <span className="font-medium text-slate-700 capitalize">{selectedSession.status}</span></span>
                      <span>Duration: <span className="font-medium text-slate-700">{formatDuration(selectedSession.startTime, selectedSession.endTime)}</span></span>
                    </div>
                  </div>
                  {getStatusIcon(selectedSession.status)}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Traces</h3>
                <div className="space-y-2">
                  {traces?.map((trace) => (
                    <button
                      key={trace.id}
                      onClick={() => handleTraceClick(trace)}
                      className={clsx(
                        'w-full card text-left hover:shadow-md transition-all',
                        selectedTrace?.id === trace.id && 'ring-2 ring-agentloop-500'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(trace.status)}
                          <span className="font-mono text-sm">{trace.id}</span>
                          <span className="badge-info text-xs">
                            {trace.toolCalls.length} tools
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-slate-500">
                            {formatDuration(trace.startTime, trace.endTime)}
                          </span>
                          <ChevronRight className="w-4 h-4 text-slate-400" />
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {selectedTrace && (
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-slate-900">Trace {selectedTrace.id}</h3>
                    <span className="font-mono text-sm text-slate-500">
                      {selectedTrace.endTime 
                        ? `${new Date(selectedTrace.endTime).getTime() - new Date(selectedTrace.startTime).getTime()}ms`
                        : 'Running...'}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {selectedTrace.toolCalls.map((tool, index) => {
                      const isExpanded = expandedTools.has(tool.id);
                      return (
                        <div key={tool.id} className="border border-slate-200 rounded-lg overflow-hidden">
                          <button
                            onClick={() => toggleTool(tool.id)}
                            className={clsx(
                              'w-full px-4 py-3 flex items-center justify-between text-left',
                              tool.success ? 'hover:bg-slate-50' : 'bg-danger-50 hover:bg-danger-100'
                            )}
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-slate-400 w-6">{index + 1}</span>
                              {tool.success ? (
                                <CheckCircle className="w-4 h-4 text-success-500" />
                              ) : (
                                <XCircle className="w-4 h-4 text-danger-500" />
                              )}
                              <span className="font-mono text-sm font-medium text-slate-900">
                                {tool.name}
                              </span>
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="text-xs text-slate-500">{tool.duration}ms</span>
                              {isExpanded ? (
                                <ChevronDown className="w-4 h-4 text-slate-400" />
                              ) : (
                                <ChevronRight className="w-4 h-4 text-slate-400" />
                              )}
                            </div>
                          </button>

                          {isExpanded && (
                            <div className="px-4 py-3 bg-slate-50 border-t border-slate-200">
                              <div className="space-y-3 text-sm">
                                <div>
                                  <span className="text-slate-500">Arguments:</span>
                                  <pre className="mt-1 p-2 bg-white rounded border border-slate-200 font-mono text-xs overflow-x-auto">
                                    {JSON.stringify(tool.arguments, null, 2)}
                                  </pre>
                                </div>
                                {tool.result && (
                                  <div>
                                    <span className="text-slate-500">Result:</span>
                                    <pre className="mt-1 p-2 bg-white rounded border border-slate-200 font-mono text-xs overflow-x-auto">
                                      {JSON.stringify(tool.result, null, 2)}
                                    </pre>
                                  </div>
                                )}
                                {tool.error && (
                                  <div>
                                    <span className="text-danger-600 font-medium">Error:</span>
                                    <pre className="mt-1 p-2 bg-danger-50 rounded border border-danger-200 font-mono text-xs text-danger-700">
                                      {tool.error}
                                    </pre>
                                  </div>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}