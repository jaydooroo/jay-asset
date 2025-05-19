// src/components/TransactionList.jsx
import React from "react";

const transactions = [
  {
    date: "2025-05-01",
    asset: "AAPL",
    type: "Buy",
    amount: "10",
    value: "$1,450",
  },
  {
    date: "2025-04-25",
    asset: "BTC",
    type: "Sell",
    amount: "0.05",
    value: "$2,300",
  },
  {
    date: "2025-04-15",
    asset: "ETH",
    type: "Buy",
    amount: "0.5",
    value: "$1,100",
  },
];

export default function TransactionList() {
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-2xl font-semibold mb-4">Recent Transactions</h2>
      <table className="w-full text-left">
        <thead>
          <tr className="border-b">
            <th className="py-2">Date</th>
            <th>Asset</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, idx) => (
            <tr key={idx} className="hover:bg-gray-100">
              <td className="py-2">{tx.date}</td>
              <td>{tx.asset}</td>
              <td>{tx.type}</td>
              <td>{tx.amount}</td>
              <td>{tx.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
