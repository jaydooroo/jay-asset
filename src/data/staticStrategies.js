// Static strategies are computed entirely on the frontend (no backend call).
// Values are target percentages that get converted into dollar amounts.
export const staticStrategies = {
  conservative: {
    name: 'Conservative',
    description: 'Low risk, stable returns',
    type: 'static',
    allocation: {
      Bonds: 60,
      Stocks: 20,
      Cash: 15,
      'Real Estate': 5,
    },
  },
  balanced: {
    name: 'Balanced',
    description: 'Moderate risk, balanced growth',
    type: 'static',
    allocation: {
      Stocks: 40,
      Bonds: 30,
      'Real Estate': 15,
      Commodities: 10,
      Cash: 5,
    },
  },
  aggressive: {
    name: 'Aggressive',
    description: 'High risk, maximum growth potential',
    type: 'static',
    allocation: {
      Stocks: 70,
      'Real Estate': 15,
      Commodities: 10,
      Bonds: 5,
    },
  },
};
