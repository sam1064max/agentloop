import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart2, GitBranch, AlertCircle } from 'lucide-react';
import { fetchPathAnalysis, fetchInsights } from '../services/api';
import WorkflowPath from '../components/WorkflowPath';
import DataTable, { Column } from '../components/DataTable';
import type { PathAnalysis, PathNode, RootCauseInsight } from '../types';
import clsx from 'clsx';

export default function WorkflowExplorer() {
  const { data: analysis, isLoading: analysisLoading } = useQuery({
    queryKey: ['pathAnalysis'],
    queryFn: fetchPathAnalysis,
  });

  const { data: insights } = useQuery({
    queryKey: ['insights'],
    queryFn: fetchInsights,
  });

  const [selectedNode, setSelectedNode] = useState<PathNode | null>(null);

  if (analysisLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="card h-96" />
        <div className="card h-64" />
      </div>
    );
  }

  if (!analysis) {
    return <div className="text-slate-500">Failed to load workflow analysis</div>;
  }

  const handleNodeClick = (node: PathNode) => {
    setSelectedNode(node);
  };

  const columns: Column<PathNode>[] = [
    {
      key: 'name',
      header: 'Node',
      sortable: true,
    },
    {
      key: 'count',
      header: 'Sessions',
      sortable: true,
      render: (item) => item.count.toLocaleString(),
    },
    {
      key: 'successRate',
      header: 'Success Rate',
      sortable: true,
      render: (item) => (
        <span className={clsx(
          'font-medium',
          item.successRate >= 95 ? 'text-success-600' :
          item.successRate >= 85 ? 'text-warning-600' :
          'text-danger-600'
        )}>
          {item.successRate}%
        </span>
      ),
    },
    {
      key: 'avgDuration',
      header: 'Avg Duration',
      sortable: true,
      render: (item) => `${item.avgDuration}ms`,
    },
  ];

  const insightColumns: Column<RootCauseInsight>[] = [
    {
      key: 'type',
      header: 'Type',
      render: (item) => (
        <span className={clsx(
          'badge',
          item.type === 'error' && 'badge-danger',
          item.type === 'bottleneck' && 'badge-warning',
          item.type === 'pattern' && 'badge-info',
          item.type === 'anomaly' && 'bg-purple-100 text-purple-700'
        )}>
          {item.type}
        </span>
      ),
    },
    {
      key: 'title',
      header: 'Title',
      render: (item) => <span className="font-medium text-slate-900">{item.title}</span>,
    },
    {
      key: 'affectedTraces',
      header: 'Affected',
      render: (item) => item.affectedTraces.toLocaleString(),
    },
    {
      key: 'impactScore',
      header: 'Impact',
      render: (item) => (
        <div className="flex items-center gap-2">
          <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={clsx(
                'h-full rounded-full',
                item.impactScore >= 80 ? 'bg-danger-500' :
                item.impactScore >= 60 ? 'bg-warning-500' :
                'bg-agentloop-500'
              )}
              style={{ width: `${item.impactScore}%` }}
            />
          </div>
          <span className="text-sm text-slate-600">{item.impactScore}</span>
        </div>
      ),
    },
    {
      key: 'confidence',
      header: 'Confidence',
      render: (item) => `${(item.confidence * 100).toFixed(0)}%`,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Workflow Explorer</h1>
        <p className="text-slate-500 mt-1">Analyze execution paths and identify bottlenecks</p>
      </div>

      <WorkflowPath analysis={analysis} onNodeClick={handleNodeClick} />

      {selectedNode && (
        <div className="card border-agentloop-200 bg-agentloop-50">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">{selectedNode.name}</h3>
              <div className="mt-2 flex items-center gap-6 text-sm">
                <span className="text-slate-600">
                  <strong>{selectedNode.count.toLocaleString()}</strong> sessions
                </span>
                <span className="text-slate-600">
                  <strong>{selectedNode.successRate}%</strong> success rate
                </span>
                <span className="text-slate-600">
                  <strong>{selectedNode.avgDuration}ms</strong> avg duration
                </span>
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <BarChart2 className="w-5 h-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">Path Nodes</h2>
          </div>
          <DataTable
            data={analysis.nodes}
            columns={columns}
            keyExtractor={(item) => item.id}
            searchable
            searchPlaceholder="Search nodes..."
            pageSize={10}
            onRowClick={handleNodeClick}
          />
        </div>

        <div>
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-5 h-5 text-slate-600" />
            <h2 className="text-lg font-semibold text-slate-900">Root Cause Insights</h2>
          </div>
          {insights && insights.length > 0 ? (
            <DataTable
              data={insights}
              columns={insightColumns}
              keyExtractor={(item) => item.id}
              pageSize={10}
            />
          ) : (
            <div className="card text-center text-slate-500 py-12">
              No insights available
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <GitBranch className="w-5 h-5 text-slate-600" />
          <h2 className="text-lg font-semibold text-slate-900">Most Common Path</h2>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {analysis.mostCommonPath.map((step, index) => (
            <div key={index} className="flex items-center gap-2">
              <span className="px-3 py-1.5 bg-agentloop-100 text-agentloop-700 rounded-lg text-sm font-medium">
                {step}
              </span>
              {index < analysis.mostCommonPath.length - 1 && (
                <span className="text-slate-400">→</span>
              )}
            </div>
          ))}
        </div>
        <div className="mt-4 text-sm text-slate-500">
          Average path length: <strong>{analysis.avgPathLength}</strong> steps
        </div>
      </div>
    </div>
  );
}