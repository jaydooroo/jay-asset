const METADATA = {
  SPY: {
    name: 'SPDR S&P 500 ETF Trust',
    assetType: 'US Large-Cap Equity',
    market: 'United States',
    role: 'Offensive',
  },
  QQQ: {
    name: 'Invesco QQQ Trust',
    assetType: 'US Large-Cap Growth Equity',
    market: 'United States',
    role: 'Offensive',
  },
  IWM: {
    name: 'iShares Russell 2000 ETF',
    assetType: 'US Small-Cap Equity',
    market: 'United States',
    role: 'Offensive',
  },
  VGK: {
    name: 'Vanguard FTSE Europe ETF',
    assetType: 'Developed International Equity',
    market: 'Europe',
    role: 'Offensive',
  },
  EWJ: {
    name: 'iShares MSCI Japan ETF',
    assetType: 'Developed International Equity',
    market: 'Japan',
    role: 'Offensive',
  },
  EEM: {
    name: 'iShares MSCI Emerging Markets ETF',
    assetType: 'Emerging Markets Equity',
    market: 'Global Emerging Markets',
    role: 'Offensive',
  },
  VNQ: {
    name: 'Vanguard Real Estate ETF',
    assetType: 'US REITs',
    market: 'United States',
    role: 'Offensive',
  },
  GLD: {
    name: 'SPDR Gold Shares',
    assetType: 'Gold Commodity',
    market: 'Global',
    role: 'Offensive',
  },
  DBC: {
    name: 'Invesco DB Commodity Index Tracking Fund',
    assetType: 'Broad Commodities',
    market: 'Global',
    role: 'Offensive',
  },
  HYG: {
    name: 'iShares iBoxx $ High Yield Corporate Bond ETF',
    assetType: 'US High Yield Bonds',
    market: 'United States',
    role: 'Offensive',
  },
  LQD: {
    name: 'iShares iBoxx $ Investment Grade Corporate Bond ETF',
    assetType: 'Investment Grade Corporate Bonds',
    market: 'United States',
    role: 'Defensive',
  },
  IEF: {
    name: 'iShares 7-10 Year Treasury Bond ETF',
    assetType: 'US Treasury Bonds',
    market: 'United States',
    role: 'Defensive',
  },
  EFA: {
    name: 'iShares MSCI EAFE ETF',
    assetType: 'Developed International Equity',
    market: 'Europe / Asia / Far East',
    role: 'Offensive',
  },
  AGG: {
    name: 'iShares Core U.S. Aggregate Bond ETF',
    assetType: 'US Core Bonds',
    market: 'United States',
    role: 'Defensive',
  },
  SHY: {
    name: 'iShares 1-3 Year Treasury Bond ETF',
    assetType: 'Short-Term US Treasuries',
    market: 'United States',
    role: 'Defensive',
  },
};

export const getTickerMetadata = (ticker) => {
  const normalized = String(ticker || '').toUpperCase();
  const found = METADATA[normalized];

  return {
    ticker: normalized,
    name: found?.name || normalized,
    assetType: found?.assetType || 'ETF',
    market: found?.market || 'Global',
    role: found?.role || 'N/A',
  };
};
