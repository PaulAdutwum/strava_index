import {
  Bar,
  CartesianGrid,
  ComposedChart,
  LabelList,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ShardCountRow } from "../api";

type Props = {
  data: ShardCountRow[];
  loading: boolean;
  error?: string;
};

export default function ShardCount({ data, loading, error }: Props) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <p className="panel-label">Top 5 Shard Users</p>
          <h2>Shard count</h2>
        </div>
      </header>

      {loading ? (
        <div className="panel-loading">Loading shard data…</div>
      ) : error ? (
        <div className="panel-error">{error}</div>
      ) : (
        <div className="panel-content">
          <ResponsiveContainer width="100%" height={360}>
            <ComposedChart
              data={data}
              margin={{ top: 24, right: 22, left: -20, bottom: 24 }}
            >
              <defs>
                <linearGradient id="shardGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22c55e" stopOpacity={0.92} />
                  <stop offset="100%" stopColor="#4ade80" stopOpacity={0.22} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" vertical={false} />
              <XAxis
                dataKey="index"
                tick={{ fill: "#cbd5e1", fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                interval={0}
                angle={-20}
                dy={10}
              />
              <YAxis
                yAxisId="left"
                tick={{ fill: "#cbd5e1", fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                width={56}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                tick={{ fill: "#cbd5e1", fontSize: 12 }}
                tickLine={false}
                axisLine={false}
                width={56}
              />
              <Tooltip
                contentStyle={{
                  background: "#0f172a",
                  border: "1px solid #334155",
                  color: "#e2e8f0",
                }}
              />
              <Legend wrapperStyle={{ color: "#cbd5e1" }} />
              <Bar
                yAxisId="left"
                dataKey="shards"
                name="Shard count"
                fill="url(#shardGradient)"
                radius={[8, 8, 0, 0]}
              >
                <LabelList
                  dataKey="shards"
                  position="top"
                  fill="#e2e8f0"
                  style={{ fontSize: 12 }}
                />
              </Bar>
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="size_gb"
                name="Size (GB)"
                stroke="#7c3aed"
                strokeWidth={3}
                dot={{ r: 4, strokeWidth: 2, fill: "#7c3aed" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="panel-summary">
            {data.map((item) => (
              <div key={item.index} className="summary-item">
                <span>{item.index}</span>
                <strong>{item.shards} shards</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
