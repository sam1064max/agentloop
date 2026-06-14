import { useQuery } from '@tanstack/react-query';
import { Activity, Users, ThumbsUp, AlertTriangle } from 'lucide-react';
import { fetchAnalytics } from '../services/api';
import MetricCard from '../components/MetricCard';
import LineChart from '../components/LineChart';
import PieChart from '../components/PieChart';

export default function Overview() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: fetchAnalytics,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card h-32" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card h-80" />
          <div className="card h-80" />
        </div>
      </div>
    );
  }

  if (!analytics) {
    return <div className="text-slate-500">Failed to load analytics data</div>;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Dashboard Overview</h1>
          <p className="text-slate-500 mt-1">Real-time insights into AI agent performance</p>
        </div>
        <div className="text-sm text-slate-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Sessions"
          value={analytics.sessionsCount.toLocaleString()}
          trend={analytics.sessionsTrend}
          trendLabel="vs last week"
          icon={<Users className="w-6 h-6" />}
        />
        <MetricCard
          title="Success Rate"
          value={`${analytics.successRate}%`}
          trend={analytics.successRateTrend}
          trendLabel="vs last week"
          icon={<ThumbsUp className="w-6 h-6" />}
        />
        <MetricCard
          title="Escalation Rate"
          value={`${analytics.escalationRate}%`}
          trend={analytics.escalationRateTrend}
          trendLabel="vs last week"
          icon={<AlertTriangle className="w-6 h-6" />}
        />
        <MetricCard
          title="Customer Satisfaction"
          value={`${analytics.csat}/5`}
          trend={analytics.csatTrend}
          trendLabel="vs last week"
          icon={<Activity className="w-6 h-6" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart
          data={analytics.sessionsOverTime}
          dataKey="value"
          name="Sessions"
          color="#0d8bf5"
          height={320}
          showLegend
        />
        <LineChart
          data={analytics.successRateOverTime}
          dataKey="value"
          name="Success Rate"
          color="#22c55e"
          height={320}
          showLegend
          formatYAxis={(value) => `${value}%`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Outcome Distribution</h3>
          <PieChart
            data={analytics.outcomesByType}
            height={280}
            innerRadius={60}
            outerRadius={100}
          />
        </div>
        <div className="lg:col-span-2">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Tool Usage Statistics</h3>
          <div className="card">
            <div className="space-y-4">
              {analytics.toolUsageByAgent.map((tool, index) => (
                <div key={tool.name} className="flex items-center gap-4">
                  <div className="w-32 text-sm font-medium text-slate-700 truncate">
                    {tool.name}
                  </div>
                  <div className="flex-1">
                    <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-agentloop-500 rounded-full transition-all duration-500"
                        style={{ width: `${(tool.count / analytics.toolUsageByAgent[0].count) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div className="w-20 text-sm text-slate-600 text-right">
                    {tool.count.toLocaleString()}
                  </div>
                  <div className="w-20 text-sm text-slate-500 text-right">
                    {tool.avgDuration}ms
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}