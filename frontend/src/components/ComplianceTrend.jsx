import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function ComplianceTrend({ data }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">30-DAY PERFORMANCE</p>
          <h2>Compliance trend</h2>
        </div>
        <span className="chart-legend"><i /> Overall score</span>
      </div>
      {data.length ? (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 16, right: 12, left: -18, bottom: 0 }}>
              <CartesianGrid stroke="#263242" strokeDasharray="3 5" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: "#8793a4", fontSize: 11 }} tickLine={false} axisLine={false} minTickGap={34} />
              <YAxis domain={[0, 100]} tick={{ fill: "#8793a4", fontSize: 11 }} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: "#17212e", border: "1px solid #2a384b", borderRadius: 8 }} />
              <Line type="monotone" dataKey="score" stroke="#54d6aa" strokeWidth={3} dot={false} activeDot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : <p className="empty-note">No compliance snapshots yet.</p>}
    </section>
  );
}
