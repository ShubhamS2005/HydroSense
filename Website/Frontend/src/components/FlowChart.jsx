import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useState } from "react";

function FlowChart({ data }) {
  const [history, setHistory] = useState([]);

  // 👉 Instead of useEffect, update directly (safe here)
  if (data) {
    if (history.length === 0 || history[history.length - 1] !== data) {
      const updated = [...history, data].slice(-20);
      setHistory(updated);
    }
  }

  return (
    <div className="bg-[#1e293b] p-6 rounded-2xl shadow mt-6">
      <h2 className="text-lg font-semibold mb-4 text-blue-400">
        Flow Trends (Real-Time)
      </h2>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={history}>
          <CartesianGrid stroke="#444" strokeDasharray="5 5" />

          <XAxis dataKey="timestamp" stroke="#ccc" />

          <YAxis stroke="#ccc" />

          <Tooltip />

          <Line type="monotone" dataKey="flow1" stroke="#38bdf8" dot={false} />
          <Line type="monotone" dataKey="flow2" stroke="#22c55e" dot={false} />
          <Line type="monotone" dataKey="flow3" stroke="#facc15" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default FlowChart;