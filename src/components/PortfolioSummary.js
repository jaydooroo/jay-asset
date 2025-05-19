import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const sampleData = [
  { date: "Jan", value: 10000 },
  { date: "Feb", value: 10500 },
  { date: "Mar", value: 11000 },
  { date: "Apr", value: 10800 },
  { date: "May", value: 11500 },
];

export default function PortfolioSummary() {
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-2xl font-semibold mb-4">Portfolio Performance</h2>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={sampleData}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#4B90F3"
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
} 