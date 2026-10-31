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
          'Custom tickers need stored price history before they can be used in calculations.',
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
          'Custom tickers need stored price history before they can be used in calculations.',
        ],
      },
    ],
  },
  cdm: {
    title: 'CDM (Composite Dual Momentum)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Splits the portfolio into 4 sleeves (equity, credit, real estate, hedge), each with 25% target weight.',
          'Within each sleeve, compares 12-month returns of two ETFs and picks the stronger one.',
        ],
      },
      {
        heading: 'Cash filter',
        bullets: [
          'Uses BIL as a cash proxy.',
          'If both sleeve ETFs underperform BIL over the same lookback, that sleeve allocates to BIL.',
        ],
      },
      {
        heading: 'Default sleeve pairs',
        bullets: [
          'Equity: SPY vs EFA',
          'Credit: LQD vs HYG',
          'Real estate: VNQ vs REM',
          'Hedge: TLT vs GLD',
        ],
      },
    ],
  },
  daa: {
    title: 'DAA (Defensive Asset Allocation)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          'Uses two canary assets (VWO, BND) as early-warning signals for market downturns.',
          'Allocates equally to the top N offensive ETFs when the market is healthy, and shifts to the best defensive bond otherwise.',
          'Momentum score = 12×R1 + 4×R3 + 2×R6 + 1×R12',
        ],
      },
      {
        heading: 'Canary signal',
        bullets: [
          'Both VWO & BND positive → 100% offensive',
          'One of VWO / BND positive → 50% offensive, 50% defensive',
          'Both VWO & BND negative → 0% offensive, 100% defensive',
        ],
      },
      {
        heading: 'Universe',
        bullets: [
          'Offensive (12 ETFs): SPY, QQQ, IWM, VGK, EWJ, EEM, VNQ, GLD, DBC, HYG, LQD, TLT',
          'Defensive (3 ETFs): LQD, IEF, SHY',
          'Canary: VWO, BND',
        ],
      },
      {
        heading: 'Historical performance (1973–2021)',
        bullets: [
          'CAGR ~14.7%,  MDD ~−12%,  Sharpe 1.12',
          'Portfolio lost more than 10% only twice in ~50 years.',
        ],
      },
    ],
  },
  gem: {
    title: 'GEM (Dual Momentum)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          "Gary Antonacci's Global Equities Momentum. Holds 100% in a single asset each month.",
          'Absolute momentum: if SPY beat cash (BIL) over 12 months, stay in stocks; otherwise move to bonds (AGG).',
          'Relative momentum: when in stocks, pick the stronger of US (SPY) and international (EFA).',
        ],
      },
      {
        heading: 'Trade-offs',
        bullets: [
          'Very simple and avoids long bear markets, but holding one asset means big swings.',
          'Can lag after sharp V-shaped recoveries because the 12-month signal reacts slowly.',
        ],
      },
    ],
  },
  gtaa: {
    title: 'GTAA (Faber Trend Following)',
    rebalanceFrequency: 'Monthly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          "Mebane Faber's timing model: 20% each in US stocks (SPY), international stocks (EFA), Treasuries (IEF), commodities (DBC) and REITs (VNQ).",
          'At each month-end, a slice holds its asset only if the price is above its 10-month moving average; otherwise that slice goes to cash (BIL).',
        ],
      },
      {
        heading: 'Trade-offs',
        bullets: [
          'Cuts drawdowns in long declines while keeping most of the upside.',
          'In choppy sideways markets it can switch in and out and lose a little each time.',
        ],
      },
    ],
  },
  laa: {
    title: 'LAA (Lethargic Asset Allocation)',
    rebalanceFrequency: 'Monthly (changes rarely)',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          '75% stays fixed: 25% each in large-cap value (IWD), gold (GLD) and 7-10y Treasuries (IEF).',
          'The last 25% holds Nasdaq (QQQ) while the S&P 500 is above its 200-day moving average, and short Treasuries (SHY) otherwise.',
        ],
      },
      {
        heading: 'Simplified version',
        bullets: [
          "Wouter Keller's original switches to SHY only when the price signal AND rising US unemployment agree.",
          'This app does not store unemployment data, so it uses the price signal alone and may switch to SHY more often.',
        ],
      },
    ],
  },
  sixty_forty: {
    title: '60/40 Portfolio',
    rebalanceFrequency: 'Yearly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          '60% US stocks (SPY), 40% US investment-grade bonds (AGG).',
          'Once a year, sell what grew and buy what shrank to get back to 60/40.',
        ],
      },
      {
        heading: 'Good for',
        bullets: ['Investors who want one simple, widely used benchmark portfolio.'],
      },
      {
        heading: 'Trade-offs',
        bullets: ['Stocks and bonds can fall together when inflation rises (as in 2022).'],
      },
    ],
  },
  permanent: {
    title: 'Permanent Portfolio',
    rebalanceFrequency: 'Yearly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          "Harry Browne's portfolio: 25% each in stocks (SPY), long-term Treasuries (TLT), gold (GLD) and cash (BIL).",
          'Each asset is meant to do well in a different economy: growth, deflation, inflation and recession.',
        ],
      },
      {
        heading: 'Trade-offs',
        bullets: [
          'Small drawdowns and a calm ride, but lower long-term returns than stock-heavy portfolios.',
        ],
      },
    ],
  },
  all_weather: {
    title: 'All Weather Portfolio',
    rebalanceFrequency: 'Yearly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          "Popular simplified version of Ray Dalio's risk-parity idea.",
          'Stocks 30% (SPY), long Treasuries 40% (TLT), intermediate Treasuries 15% (IEF), gold 7.5% (GLD), commodities 7.5% (DBC).',
          'Heavy bond weight balances the risk of the stock slice.',
        ],
      },
      {
        heading: 'Trade-offs',
        bullets: ['Sensitive to rising interest rates because of the large long-bond weight.'],
      },
    ],
  },
  golden_butterfly: {
    title: 'Golden Butterfly',
    rebalanceFrequency: 'Yearly',
    sections: [
      {
        heading: 'What it does',
        bullets: [
          '20% each in large-cap stocks (SPY), small-cap value (VBR), long Treasuries (TLT), short Treasuries (SHY) and gold (GLD).',
          'A Permanent Portfolio variant with more stocks for extra growth.',
        ],
      },
      {
        heading: 'Trade-offs',
        bullets: ['Usually more growth than the Permanent Portfolio, with slightly deeper drawdowns.'],
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
    ],
  },
  cdm: {
    title: 'CDM (종합 듀얼 모멘텀)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '전략 개요',
        bullets: [
          '포트폴리오를 4개 파트(주식, 회사채, 부동산, 위기대응)로 나누고 각 파트를 25%로 운용합니다.',
          '각 파트에서 2개 ETF의 최근 12개월 수익률을 비교해 더 강한 ETF를 선택합니다.',
        ],
      },
      {
        heading: '현금 필터',
        bullets: [
          '현금 대체 자산으로 BIL을 사용합니다.',
          '파트 내 두 ETF 모두 BIL보다 수익률이 낮으면 해당 파트는 BIL에 배분합니다.',
        ],
      },
      {
        heading: '기본 파트 구성',
        bullets: [
          '주식: SPY vs EFA',
          '회사채: LQD vs HYG',
          '부동산: VNQ vs REM',
          '위기대응: TLT vs GLD',
        ],
      },
    ],
  },
  daa: {
    title: 'DAA (방어적 자산 배분)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '카나리아 자산(VWO, BND)의 모멘텀으로 시장 위기를 조기 감지합니다.',
          '시장이 건강할 때는 상위 N개 공격 ETF에 균등 배분, 위기 신호 시 최고 방어 자산으로 이동합니다.',
          '모멘텀 점수 = 12×1개월 수익 + 4×3개월 수익 + 2×6개월 수익 + 1×12개월 수익',
        ],
      },
      {
        heading: '카나리아 신호 체계',
        bullets: [
          'VWO, BND 둘 다 양수 → 공격 자산 100%',
          'VWO 또는 BND 중 하나만 양수 → 공격 자산 50%, 방어 자산 50%',
          'VWO, BND 둘 다 음수 → 공격 자산 0%, 방어 자산 100%',
        ],
      },
      {
        heading: '자산군',
        bullets: [
          '공격 자산 (12개): SPY, QQQ, IWM, VGK, EWJ, EEM, VNQ, GLD, DBC, HYG, LQD, TLT',
          '방어 자산 (3개): LQD, IEF, SHY',
          '카나리아: VWO, BND',
        ],
      },
      {
        heading: '백테스트 성과 (1973–2021)',
        bullets: [
          '연복리 수익률 약 14.7%,  최대낙폭 약 −12%,  샤프지수 1.12',
          '약 50년간 포트폴리오 손실이 10% 이상 난 경우는 단 2번.',
        ],
      },
    ],
  },
  gem: {
    title: 'GEM (듀얼 모멘텀)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '게리 안토나치의 글로벌 주식 모멘텀 전략입니다. 매달 한 자산에 100% 투자합니다.',
          '절대 모멘텀: 최근 12개월 동안 SPY가 현금(BIL)보다 많이 올랐으면 주식, 아니면 채권(AGG)을 보유합니다.',
          '상대 모멘텀: 주식을 보유할 때는 미국(SPY)과 해외(EFA) 중 더 강한 쪽을 고릅니다.',
        ],
      },
      {
        heading: '장단점',
        bullets: [
          '규칙이 아주 단순하고 긴 하락장을 피할 수 있지만, 한 자산만 보유해서 등락 폭이 큽니다.',
          '12개월 신호라 반응이 느려서, 급락 후 급반등하는 장에서는 뒤처질 수 있습니다.',
        ],
      },
    ],
  },
  gtaa: {
    title: 'GTAA (파버 추세추종)',
    rebalanceFrequency: '월간',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '메브 파버의 타이밍 모델입니다. 미국 주식(SPY), 해외 주식(EFA), 국채(IEF), 원자재(DBC), 리츠(VNQ)에 20%씩 나눕니다.',
          '매월 말, 각 자산의 가격이 10개월 이동평균보다 높으면 보유하고, 낮으면 그 몫은 현금(BIL)으로 바꿉니다.',
        ],
      },
      {
        heading: '장단점',
        bullets: [
          '긴 하락장에서 손실을 크게 줄이면서 상승장 수익은 대부분 가져갑니다.',
          '횡보장에서는 들어갔다 나왔다를 반복하며 조금씩 손해를 볼 수 있습니다.',
        ],
      },
    ],
  },
  laa: {
    title: 'LAA (게으른 자산배분)',
    rebalanceFrequency: '월간 (거의 바뀌지 않음)',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '75%는 고정입니다: 미국 대형 가치주(IWD), 금(GLD), 7~10년 국채(IEF)에 25%씩.',
          '나머지 25%는 S&P500이 200일 이동평균 위에 있으면 나스닥(QQQ), 아래면 단기 국채(SHY)를 보유합니다.',
        ],
      },
      {
        heading: '단순화 버전',
        bullets: [
          '원래 켈러의 전략은 가격 신호와 함께 미국 실업률이 오를 때만 SHY로 바꿉니다.',
          '이 앱에는 실업률 데이터가 없어서 가격 신호만 사용합니다. 그래서 원래보다 SHY로 더 자주 바뀔 수 있습니다.',
        ],
      },
    ],
  },
  sixty_forty: {
    title: '60/40 포트폴리오',
    rebalanceFrequency: '연 1회',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '미국 주식(SPY) 60%, 미국 우량 채권(AGG) 40%.',
          '1년에 한 번, 많이 오른 쪽을 팔고 덜 오른 쪽을 사서 60:40으로 되돌립니다.',
        ],
      },
      {
        heading: '이런 분께 맞습니다',
        bullets: ['가장 널리 쓰이는 단순한 기본 포트폴리오를 원하는 분.'],
      },
      {
        heading: '장단점',
        bullets: ['물가가 오를 때는(2022년처럼) 주식과 채권이 함께 떨어질 수 있습니다.'],
      },
    ],
  },
  permanent: {
    title: '영구 포트폴리오',
    rebalanceFrequency: '연 1회',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '해리 브라운의 포트폴리오: 주식(SPY), 장기 국채(TLT), 금(GLD), 현금(BIL)에 25%씩.',
          '경기 호황, 디플레이션, 인플레이션, 불황 중 어떤 상황에서도 하나는 잘 버티도록 설계됐습니다.',
        ],
      },
      {
        heading: '장단점',
        bullets: ['낙폭이 작고 마음이 편하지만, 주식 비중이 높은 포트폴리오보다 장기 수익률은 낮습니다.'],
      },
    ],
  },
  all_weather: {
    title: '올웨더 포트폴리오',
    rebalanceFrequency: '연 1회',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '레이 달리오의 위험 균형 아이디어를 단순하게 만든 대중적인 버전입니다.',
          '주식 30%(SPY), 장기 국채 40%(TLT), 중기 국채 15%(IEF), 금 7.5%(GLD), 원자재 7.5%(DBC).',
          '채권 비중을 크게 둬서 주식의 위험과 균형을 맞춥니다.',
        ],
      },
      {
        heading: '장단점',
        bullets: ['장기 채권 비중이 커서 금리가 오를 때 약합니다.'],
      },
    ],
  },
  golden_butterfly: {
    title: '골든 버터플라이',
    rebalanceFrequency: '연 1회',
    sections: [
      {
        heading: '무엇을 하는 전략인가',
        bullets: [
          '대형주(SPY), 소형 가치주(VBR), 장기 국채(TLT), 단기 국채(SHY), 금(GLD)에 20%씩.',
          '영구 포트폴리오에 주식을 더 넣어 성장성을 높인 변형입니다.',
        ],
      },
      {
        heading: '장단점',
        bullets: ['보통 영구 포트폴리오보다 수익은 높고, 낙폭은 조금 더 큽니다.'],
      },
    ],
  },
};
