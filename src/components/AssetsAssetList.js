// src/components/AssetList.jsx
import React from "react";
import AssetCard from "./AssetCard";

const assets = [
  { symbol: "AAPL", name: "Apple Inc.", allocation: "25%", value: "$2,875" },
  {
    symbol: "GOOGL",
    name: "Alphabet Inc.",
    allocation: "20%",
    value: "$2,300",
  },
  { symbol: "BTC", name: "Bitcoin", allocation: "30%", value: "$3,450" },
  { symbol: "ETH", name: "Ethereum", allocation: "15%", value: "$1,725" },
  {
    symbol: "BND",
    name: "Total Bond Market ETF",
    allocation: "10%",
    value: "$575",
  },
];

export default function AssetList() {
  return (
    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      {assets.map((asset) => (
        <AssetCard key={asset.symbol} {...asset} />
      ))}
    </div>
  );
}
