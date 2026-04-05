import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function RankChart({ data }) {
  const chartData = [...data].reverse().map((d) => ({
    date: d.date,
    position: d.position,
  }));

  return (
    <div className="bg-gray-900 rounded-lg p-5 border border-gray-800">
      <h4 className="font-semibold mb-4">Rank History</h4>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
          <YAxis reversed stroke="#6b7280" fontSize={12} domain={[1, "auto"]} />
          <Tooltip
            contentStyle={{ backgroundColor: "#1f2937", border: "1px solid #374151", borderRadius: "8px" }}
            labelStyle={{ color: "#9ca3af" }}
          />
          <Line type="monotone" dataKey="position" stroke="#3b82f6" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
