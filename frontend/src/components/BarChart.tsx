import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';
import clsx from 'clsx';

interface BarChartProps {
  data: Record<string, unknown>[];
  dataKey: string;
  name?: string;
  color?: string;
  height?: number;
  showGrid?: boolean;
  showLegend?: boolean;
  layout?: 'vertical' | 'horizontal';
  formatXAxis?: (value: string) => string;
  formatYAxis?: (value: number) => string;
}

const COLORS = [
  '#0d8bf5',
  '#22c55e',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
];

export default function BarChart({
  data,
  dataKey,
  name,
  color,
  height = 300,
  showGrid = true,
  showLegend = false,
  layout,
  formatXAxis,
  formatYAxis,
}: BarChartProps) {
  return (
    <div className="card">
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart
          data={data}
          layout={layout}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          {showGrid && (
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          )}
          {layout === 'vertical' ? (
            <>
              <XAxis
                type="number"
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickLine={{ stroke: '#e2e8f0' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickFormatter={formatXAxis as (value: string) => string}
              />
              <YAxis
                type="category"
                dataKey={Object.keys(data[0] || {})[0]}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickLine={{ stroke: '#e2e8f0' }}
                axisLine={{ stroke: '#e2e8f0' }}
                width={100}
              />
            </>
          ) : (
            <>
              <XAxis
                dataKey={Object.keys(data[0] || {})[0]}
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickLine={{ stroke: '#e2e8f0' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickFormatter={formatXAxis}
              />
              <YAxis
                tick={{ fontSize: 12, fill: '#64748b' }}
                tickLine={{ stroke: '#e2e8f0' }}
                axisLine={{ stroke: '#e2e8f0' }}
                tickFormatter={formatYAxis}
              />
            </>
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            labelStyle={{ color: '#334155', fontWeight: 500 }}
          />
          {showLegend && (
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="circle"
            />
          )}
          <Bar
            dataKey={dataKey}
            name={name}
            fill={color || '#0d8bf5'}
            radius={[4, 4, 0, 0]}
          >
            {!color &&
              data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  );
}