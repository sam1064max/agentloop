import { useQuery } from '@tanstack/react-query';
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { fetchAgentComparisons } from '../services/api';
import BarChart from '../components/BarChart';
import DataTable, { Column } from '../components/DataTable';
import type { AgentComparison } from '../types';
import clsx from 'clsx';

export default function AgentVersions() {
  const { data: comparisons, isLoading } = useQuery({
    queryKey: ['agentComparisons'],
    queryFn: fetchAgentComparisons,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="card h-64" />
        <div className="card h-96" />
      </div>
    );
  }

  if (!comparisons) {
    return <div className="text-slate-500">Failed to load agent comparison data</div>;
  }

  const chartData = comparisons.map(c => ({
    version: c.version,
    successRate: c.successRate,
    feedbackScore: c.feedbackScore * 20,
    escalationRate: c.escalationRate * 10,
  }));

  const columns: Column<AgentComparison>[] = [
    {
      key: 'version',
      header: 'Version',
      sortable: true,
      render: (item) => (
        <div className="flex items-center gap-2">
          <span className="font-mono font-medium text-agentloop-600">{item.version}</span>
          {item.trend === 'up' && <ArrowUpRight className="w-4 h-4 text-success-500" />}
          {item.trend === 'down' && <ArrowDownRight className="w-4 h-4 text-danger-500" />}
          {item.trend === 'stable' && <Minus className="w-4 h-4 text-slate-400" />}
        </div>
      ),
    },
    {
      key: 'sessionsCount',
      header: 'Sessions',
      sortable: true,
      render: (item) => item.sessionsCount.toLocaleString(),
    },
    {
      key: 'successRate',
      header: 'Success Rate',
      sortable: true,
      render: (item) => (
        <span className={clsx(
          'font-medium',
          item.successRate >= 95 ? 'text-success-600' :
          item.successRate >= 90 ? 'text-warning-600' :
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
      render: (item) => `${(item.avgDuration / 1000).toFixed(2)}s`,
    },
    {
      key: 'avgOutcomeValue',
      header: 'Avg Value',
      sortable: true,
      render: (item) => `$${item.avgOutcomeValue.toFixed(2)}`,
    },
    {
      key: 'feedbackScore',
      header: 'CSAT',
      sortable: true,
      render: (item) => (
        <span className="font-medium">{item.feedbackScore}/5</span>
      ),
    },
    {
      key: 'escalationRate',
      header: 'Escalation',
      sortable: true,
      render: (item) => (
        <span className={clsx(
          item.escalationRate <= 3 ? 'text-success-600' :
          item.escalationRate <= 5 ? 'text-warning-600' :
          'text-danger-600'
        )}>
          {item.escalationRate}%
        </span>
      ),
    },
    {
      key: 'trend',
      header: 'Trend',
      render: (item) => (
        <span className={clsx(
          'badge',
          item.trend === 'up' && 'badge-success',
          item.trend === 'down' && 'badge-danger',
          item.trend === 'stable' && 'bg-slate-100 text-slate-700'
        )}>
          {item.trend === 'up' && '↑ Improving'}
          {item.trend === 'down' && '↓ Declining'}
          {item.trend === 'stable' && '→ Stable'}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Agent Versions</h1>
        <p className="text-slate-500 mt-1">Compare performance across different agent versions</p>
      </div>

      <BarChart
        data={chartData}
        dataKey="successRate"
        name="Success Rate"
        height={320}
        showLegend
        formatYAxis={(value) => `${value}%`}
      />

      <div>
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Version Comparison</h2>
        <DataTable
          data={comparisons}
          columns={columns}
          keyExtractor={(item) => item.version}
          searchable
          searchPlaceholder="Search versions..."
          pageSize={10}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-sm font-medium text-slate-500 mb-2">Best Performing</h3>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-success-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-success-600" />
            </div>
            <div>
              <p className="font-mono font-semibold text-slate-900">
                {comparisons.reduce((a, b) => a.successRate > b.successRate ? a : b).version}
              </p>
              <p className="text-sm text-success-600">
                {Math.max(...comparisons.map(c => c.successRate))}% success rate
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-medium text-slate-500 mb-2">Fastest</h3>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-agentloop-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-agentloop-600" />
            </div>
            <div>
              <p className="font-mono font-semibold text-slate-900">
                {comparisons.reduce((a, b) => a.avgDuration < b.avgDuration ? a : b).version}
              </p>
              <p className="text-sm text-agentloop-600">
                {(Math.min(...comparisons.map(c => c.avgDuration)) / 1000).toFixed(2)}s avg
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-sm font-medium text-slate-500 mb-2">Most Used</h3>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-warning-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-warning-600" />
            </div>
            <div>
              <p className="font-mono font-semibold text-slate-900">
                {comparisons.reduce((a, b) => a.sessionsCount > b.sessionsCount ? a : b).version}
              </p>
              <p className="text-sm text-warning-600">
                {Math.max(...comparisons.map(c => c.sessionsCount)).toLocaleString()} sessions
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}