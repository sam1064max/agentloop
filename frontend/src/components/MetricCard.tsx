import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import clsx from 'clsx';

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: number;
  trendLabel?: string;
  icon?: React.ReactNode;
  formatter?: (value: number) => string;
}

export default function MetricCard({
  title,
  value,
  trend,
  trendLabel,
  icon,
  formatter,
}: MetricCardProps) {
  const trendIsPositive = trend !== undefined && trend > 0;
  const trendIsNegative = trend !== undefined && trend < 0;

  const displayValue = typeof value === 'number' && formatter ? formatter(value) : value;

  return (
    <div className="card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-2 text-3xl font-semibold text-slate-900">{displayValue}</p>
        </div>
        {icon && (
          <div className="p-3 bg-agentloop-50 rounded-lg text-agentloop-600">
            {icon}
          </div>
        )}
      </div>

      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-2">
          <div
            className={clsx(
              'flex items-center gap-1 text-sm font-medium',
              trendIsPositive && 'text-success-600',
              trendIsNegative && 'text-danger-600',
              !trendIsPositive && !trendIsNegative && 'text-slate-500'
            )}
          >
            {trendIsPositive && <TrendingUp className="w-4 h-4" />}
            {trendIsNegative && <TrendingDown className="w-4 h-4" />}
            {!trendIsPositive && !trendIsNegative && <Minus className="w-4 h-4" />}
            <span>{trend > 0 ? '+' : ''}{trend}%</span>
          </div>
          {trendLabel && <span className="text-sm text-slate-500">{trendLabel}</span>}
        </div>
      )}
    </div>
  );
}
# history: feat: add MetricCard and shared type definitions