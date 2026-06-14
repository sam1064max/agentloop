import { useQuery } from '@tanstack/react-query';
import { Lightbulb, CheckCircle, XCircle, Clock, TrendingUp, Zap, Shield, DollarSign, Gauge } from 'lucide-react';
import { fetchRecommendations } from '../services/api';
import type { Recommendation } from '../types';
import clsx from 'clsx';

const categoryIcons = {
  optimization: Zap,
  quality: Shield,
  cost: DollarSign,
  performance: Gauge,
  reliability: TrendingUp,
};

const impactColors = {
  high: 'bg-danger-100 text-danger-700 border-danger-200',
  medium: 'bg-warning-100 text-warning-700 border-warning-200',
  low: 'bg-success-100 text-success-700 border-success-200',
};

export default function Recommendations() {
  const { data: recommendations, isLoading } = useQuery({
    queryKey: ['recommendations'],
    queryFn: fetchRecommendations,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse space-y-6">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="card h-32" />
        ))}
      </div>
    );
  }

  if (!recommendations) {
    return <div className="text-slate-500">Failed to load recommendations</div>;
  }

  const statusCounts = {
    pending: recommendations.filter(r => r.status === 'pending').length,
    accepted: recommendations.filter(r => r.status === 'accepted').length,
    implemented: recommendations.filter(r => r.status === 'implemented').length,
    rejected: recommendations.filter(r => r.status === 'rejected').length,
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Recommendations</h1>
        <p className="text-slate-500 mt-1">AI-generated insights to optimize agent performance</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card flex items-center gap-3">
          <div className="p-2 bg-warning-100 rounded-lg">
            <Clock className="w-5 h-5 text-warning-600" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-slate-900">{statusCounts.pending}</p>
            <p className="text-sm text-slate-500">Pending</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="p-2 bg-agentloop-100 rounded-lg">
            <CheckCircle className="w-5 h-5 text-agentloop-600" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-slate-900">{statusCounts.accepted}</p>
            <p className="text-sm text-slate-500">Accepted</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="p-2 bg-success-100 rounded-lg">
            <CheckCircle className="w-5 h-5 text-success-600" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-slate-900">{statusCounts.implemented}</p>
            <p className="text-sm text-slate-500">Implemented</p>
          </div>
        </div>
        <div className="card flex items-center gap-3">
          <div className="p-2 bg-slate-100 rounded-lg">
            <XCircle className="w-5 h-5 text-slate-500" />
          </div>
          <div>
            <p className="text-2xl font-semibold text-slate-900">{statusCounts.rejected}</p>
            <p className="text-sm text-slate-500">Rejected</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {recommendations
          .sort((a, b) => b.impactScore - a.impactScore)
          .map((rec) => {
            const CategoryIcon = categoryIcons[rec.category];
            return (
              <div key={rec.id} className="card hover:shadow-md transition-shadow">
                <div className="flex items-start gap-4">
                  <div className={clsx(
                    'p-3 rounded-lg',
                    rec.category === 'optimization' && 'bg-yellow-100 text-yellow-700',
                    rec.category === 'quality' && 'bg-blue-100 text-blue-700',
                    rec.category === 'cost' && 'bg-green-100 text-green-700',
                    rec.category === 'performance' && 'bg-purple-100 text-purple-700',
                    rec.category === 'reliability' && 'bg-slate-100 text-slate-700'
                  )}>
                    <CategoryIcon className="w-6 h-6" />
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">{rec.title}</h3>
                        <p className="mt-1 text-slate-600">{rec.description}</p>
                      </div>

                      <div className="flex flex-col items-end gap-2">
                        <span className={clsx(
                          'px-3 py-1 rounded-full text-sm font-medium border',
                          impactColors[rec.impact]
                        )}>
                          {rec.impact} impact
                        </span>
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-1">
                            <TrendingUp className="w-4 h-4 text-slate-400" />
                            <span className="text-sm font-medium text-slate-700">
                              {rec.impactScore}
                            </span>
                          </div>
                          <span className={clsx(
                            'badge',
                            rec.status === 'pending' && 'bg-warning-100 text-warning-700',
                            rec.status === 'accepted' && 'bg-agentloop-100 text-agentloop-700',
                            rec.status === 'implemented' && 'bg-success-100 text-success-700',
                            rec.status === 'rejected' && 'bg-slate-100 text-slate-700'
                          )}>
                            {rec.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-slate-500">
                      <div className="flex items-center gap-1">
                        <Lightbulb className="w-4 h-4" />
                        <span className="capitalize">{rec.category}</span>
                      </div>
                      <div>
                        Effort: <span className="capitalize font-medium">{rec.effort}</span>
                      </div>
                      {rec.agentVersions && (
                        <div className="flex items-center gap-1">
                          <span>Versions:</span>
                          {rec.agentVersions.map(v => (
                            <span key={v} className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-xs">
                              {v}
                            </span>
                          ))}
                        </div>
                      )}
                      <div>
                        {new Date(rec.createdAt).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="mt-4 p-3 bg-slate-50 rounded-lg">
                      <p className="text-sm text-slate-600">
                        <strong>Recommendation:</strong> {rec.recommendation || 'No specific recommendation provided'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
      </div>
    </div>
  );
}