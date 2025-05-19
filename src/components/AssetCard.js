// src/components/AssetCard.jsx
import React from "react";
export default function AssetCard({ symbol, name, allocation, value }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 hover:shadow-lg transition">
      <h3 className="text-xl font-bold">{symbol}</h3>
      <p className="text-sm text-gray-500">{name}</p>
      <div className="mt-4 flex justify-between items-center">
        <span className="font-medium">Allocation: {allocation}</span>
        <span className="font-semibold">{value}</span>
      </div>
    </div>
  );
}
