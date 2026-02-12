// Educational content for each strategy shown in the UI "About" panel.
// Keyed by strategy id (e.g. "paa", "simple_momentum").
export const strategyEducation = {
  conservative: {
    title: 'Conservative (Static Allocation)',
    rebalanceFrequency: 'Quarterly (recommended)',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Allocates mostly to bonds and cash for stability.',
          'Targets lower volatility and smaller drawdowns.',
        ],
      },
      {
        heading: 'Good for',
        bullets: ['Shorter time horizons, capital preservation, or risk-averse investors.'],
      },
      {
        heading: 'Trade-offs',
        bullets: [
          'Lower expected long-term growth compared to more stock-heavy strategies.',
          'Inflation can reduce real returns if cash allocation is high.',
        ],
      },
    ],
  },
  balanced: {
    title: 'Balanced (Static Allocation)',
    rebalanceFrequency: 'Quarterly (recommended)',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Mixes stocks and bonds to balance growth and risk.',
          'Aims for smoother performance than an all-stock portfolio.',
        ],
      },
      {
        heading: 'Good for',
        bullets: ['Medium time horizons and investors who want a “middle ground”.'],
      },
      {
        heading: 'Trade-offs',
        bullets: [
          'Can still draw down during stock market declines.',
          'May lag aggressive allocations during strong bull markets.',
        ],
      },
    ],
  },
  aggressive: {
    title: 'Aggressive (Static Allocation)',
    rebalanceFrequency: 'Quarterly (recommended)',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Allocates heavily to stocks and growth assets.',
          'Targets higher expected return with higher volatility.',
        ],
      },
      {
        heading: 'Good for',
        bullets: ['Long time horizons and investors comfortable with larger swings.'],
      },
      {
        heading: 'Trade-offs',
        bullets: ['Can have large drawdowns in market crashes.', 'Requires discipline to stick with the plan.'],
      },
    ],
  },
  paa: {
    title: 'PAA (Protective Asset Allocation)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Uses momentum to pick the strongest ETFs, while shifting to a defensive bond ETF (IEF) when momentum weakens.',
          'Compares current price to a 12-month moving average (252 trading days).',
        ],
      },
      {
        heading: 'How allocation is decided',
        bullets: [
          'Compute momentum for each ETF: (Price / 12M Moving Avg) - 1.',
          'Count how many ETFs have negative momentum; more negatives → higher defensive allocation to IEF.',
          'Select Top N ETFs by momentum and allocate the offensive portion equally across them (only if momentum ≥ 0).',
        ],
      },
      {
        heading: 'Inputs you can change',
        bullets: [
          'ETF Tickers: comma-separated list (example: SPY, QQQ, IWM).',
          'Top N ETFs: number of ETFs to consider for the offensive bucket.',
          'Lookback Months: history window used for the moving average calculation.',
        ],
      },
      {
        heading: 'Data requirement',
        bullets: [
          'Uses live market data (Yahoo Finance and/or Stooq); calculations may fail if your network blocks the data source or rate-limits requests.',
        ],
      },
    ],
  },
  simple_momentum: {
    title: 'Simple Momentum (Demo)',
    rebalanceFrequency: 'Monthly (demo)',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Demonstrates momentum logic using simulated scores (no external market data).',
          'Picks the top assets with positive momentum and equal-weights them.',
        ],
      },
      {
        heading: 'Good for',
        bullets: ['Testing the UI and API flow without relying on live market data.'],
      },
    ],
  },
  vaa: {
    title: 'VAA Aggressive (Vigilant Asset Allocation)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Computes weighted momentum using 1/3/6/12-month returns.',
          'If any offensive asset momentum is negative, switches 100% to the best defensive asset.',
        ],
      },
      {
        heading: 'Universe',
        bullets: [
          'Offensive: SPY, EFA, EEM, AGG',
          'Defensive: LQD, IEF, SHY',
        ],
      },
      {
        heading: 'Data requirement',
        bullets: [
          'Requires enough historical data to compute 12-month returns.',
          'Uses live market data (Yahoo Finance and/or Stooq).',
        ],
      },
    ],
  },
};
