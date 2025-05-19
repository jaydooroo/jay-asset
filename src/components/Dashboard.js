// src/components/Dashboard.jsx
import React from "react";
import PortfolioSummary from "./PortfolioSummary";
import AssetList from "./AssetList";
import TransactionList from "./TransactionList";

const Dashboard = () => {
  // Sample data for assets
  const assets = [
    { id: 1, name: 'Stocks', type: 'Equity', value: 50000, change: 5.2 },
    { id: 2, name: 'Bonds', type: 'Fixed Income', value: 30000, change: 2.1 },
    { id: 3, name: 'Real Estate', type: 'Property', value: 200000, change: -1.5 },
    { id: 4, name: 'Crypto', type: 'Digital', value: 15000, change: 8.7 },
  ];

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <PortfolioSummary />
        <AssetList assets={assets} />
      </div>
    </div>
  );
};

export default Dashboard;
