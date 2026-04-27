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
import type { LargestIndex } from "../api";

type Props = {
  data: LargestIndex[];
  loading: boolean;
  error?: string;
};

export default function LargestIndexes({ data, loading, error }: Props) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <p className="panel-label">Top 5 Largest Indexes</p>
          <h2>Size by GB</h2>
        </div>
      </header>

      {loading ? (
        <div className="panel-loading">Loading largest indexes…</div>
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
                <linearGradient id="sizeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.92} />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.3} />
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
                dataKey="size_gb"
                name="Size (GB)"
                fill="url(#sizeGradient)"
                radius={[8, 8, 0, 0]}
              >
                <LabelList
                  dataKey="size_gb"
                  position="top"
                  formatter={(value: number) => `${value.toFixed(1)} GB`}
                  fill="#e2e8f0"
                  style={{ fontSize: 12 }}
                />
              </Bar>
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="shards"
                name="Shard count"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ r: 4, strokeWidth: 2, fill: "#22c55e" }}
              />
            </ComposedChart>
          </ResponsiveContainer>
          <div className="panel-summary">
            {data.map((item) => (
              <div key={item.index} className="summary-item">
                <span>{item.index}</span>
                <strong>{item.size_gb.toFixed(2)} GB</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
