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

export const strategyEducationKo = {
  paa: {
    title: 'PAA (보호 자산 배분)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '모멘텀 순위로 강한 ETF를 선택하고, 모멘텀이 약해지면 방어형 채권 ETF(IEF) 비중을 높입니다.',
          '현재 가격을 12개월 이동평균(252거래일)과 비교합니다.',
        ],
      },
      {
        heading: '배분 방식',
        bullets: [
          '각 ETF의 모멘텀 계산: (현재가 / 12개월 이동평균) - 1',
          '모멘텀이 음수인 ETF 수를 계산하고, 음수가 많을수록 IEF 방어 비중을 높입니다.',
          '모멘텀 상위 N개 ETF를 선택하고(모멘텀 0 이상), 공격형 비중을 동일 가중으로 배분합니다.',
        ],
      },
      {
        heading: '사용자가 바꿀 수 있는 입력값',
        bullets: [
          'ETF 티커: 쉼표 구분 목록 (예: SPY, QQQ, IWM)',
          'Top N ETFs: 공격형 버킷에 포함할 상위 ETF 개수',
          'Lookback Months: 이동평균 계산에 사용하는 과거 데이터 기간',
        ],
      },
      {
        heading: '데이터 요구사항',
        bullets: [
          '실시간 시세 데이터(Yahoo Finance, Stooq)를 사용합니다. 네트워크 차단이나 호출 제한이 있으면 계산이 실패할 수 있습니다.',
        ],
      },
    ],
  },
  vaa: {
    title: 'VAA 공격형 (경계 자산 배분)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '1/3/6/12개월 수익률의 가중 모멘텀 점수를 계산합니다.',
          '공격 자산 중 음수 모멘텀이 있으면 방어 자산 최상위 1개에 100% 배분합니다.',
        ],
      },
      {
        heading: '자산군',
        bullets: [
          '공격 자산: SPY, EFA, EEM, AGG',
          '방어 자산: LQD, IEF, SHY',
        ],
      },
      {
        heading: '데이터 요구사항',
        bullets: [
          '12개월 수익률 계산이 가능할 만큼 충분한 과거 데이터가 필요합니다.',
          '실시간 시세 데이터(Yahoo Finance, Stooq)를 사용합니다.',
        ],
      },
    ],
  },
};
