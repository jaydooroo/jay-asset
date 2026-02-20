export const translations = {
  en: {
    navbar: {
      about: 'About',
      contact: 'Contact',
      language: 'Language',
      english: 'EN',
      korean: 'KO',
    },
    about: {
      title: 'About',
      body:
        'Jay Asset Management is a small web app that calculates portfolio allocations based on different strategies (static allocations and live-data strategies like momentum-based allocation).',
      disclaimer: 'Disclaimer: This project is for educational purposes and is not financial advice.',
    },
    contact: {
      title: 'Contact',
      body: 'Add your preferred contact method here (email, GitHub, LinkedIn, etc.).',
    },
    dashboard: {
      title: 'Asset Allocation Dashboard',
      subtitle: 'Pick a strategy, tune parameters, and view allocation + momentum charts.',
      backendConnected: 'Backend Connected',
      configure: 'Configure',
      selectStrategyPrompt: 'Select a strategy from the left panel to get started.',
      investmentAmount: 'Investment Amount',
      amountPlaceholder: 'Enter amount in $',
      calculate: 'Calculate',
      calculating: 'Calculating...',
      reset: 'Reset',
      results: 'Results',
      runPrompt: 'Run a calculation to see allocation charts and a breakdown table.',
      strategy: 'Strategy',
      total: 'Total: {currency}{total}',
      missingTickers: 'Missing tickers: {tickers}',
      allocationChart: 'Allocation Chart',
      momentumChart: 'Momentum Chart',
      defensive: 'Defensive {value}%',
      offensive: 'Offensive {value}%',
      avg: 'Avg {value}%',
      selected: 'Selected {value}',
      rebalance: 'Rebalance: {value}',
      errorSelectAmount: 'Please select a strategy and enter a valid amount',
      errorSelectStrategy: 'Please select a strategy',
      performanceTitle: 'Historical Performance',
      performanceSubtitle: 'Monthly walk-forward backtest summary',
      refreshPerformance: 'Refresh',
      refreshingPerformance: 'Refreshing...',
      performanceUnavailable: 'Performance data is unavailable right now.',
      perfReturn: 'Return {value}',
      perfCagr: 'CAGR {value}',
      perfMaxDrawdown: 'Max DD {value}',
      perfVolatility: 'Volatility {value}',
      perfWinRate: 'Win Rate {value}',
      perfMonthsTested: 'Months {value}',
      perfWindow: 'Window {start} to {end}',
      perfMissingTickers: 'Performance missing tickers: {tickers}',
    },
    sidebar: {
      strategies: 'Strategies',
      searchPlaceholder: 'Search strategies...',
      all: 'All',
      static: 'Static',
      live: 'Live',
      noStrategies: 'No strategies found.',
    },
    table: {
      title: 'Allocation Table',
      asset: 'Asset',
      amount: '$',
      percent: '%',
      momentum: 'Momentum',
      unknown: '-',
    },
    strategyAbout: {
      about: 'About: {title}',
      rebalance: 'Rebalance: {value}',
    },
    config: {
      strategyParameters: 'Strategy Parameters',
      paaParameters: 'PAA Parameters',
      vaaParameters: 'VAA Parameters',
      etfTickers: 'ETF Tickers',
      etfTickersHelp: 'Comma-separated tickers (e.g., SPY, QQQ, IWM)',
      topN: 'Top N ETFs',
      topNHelp: 'Number of top-performing ETFs to consider',
      lookbackMonths: 'Lookback (Months)',
      lookbackMonthsHelp: 'Used for momentum calculation (moving average)',
      offensiveAssets: 'Offensive Assets',
      offensiveAssetsHelp: 'Comma-separated tickers (book default: SPY,EFA,EEM,AGG)',
      defensiveAssets: 'Defensive Assets',
      defensiveAssetsHelp: 'Comma-separated tickers (book default: LQD,IEF,SHY)',
    },
    chart: {
      allocation: 'Allocation',
      more: '+{count} more',
      topMomentum: 'Top {count} momentum scores',
    },
    strategies: {
      paa: {
        name: 'PAA (Protective Asset Allocation)',
        description:
          'Ranks ETFs by momentum and allocates to top assets, while shifting to defensive bonds when momentum weakens.',
      },
      vaa: {
        name: 'VAA Aggressive (Vigilant Asset Allocation)',
        description:
          'Uses weighted 1/3/6/12-month momentum and rotates between offensive and defensive assets.',
      },
    },
  },
  ko: {
    navbar: {
      about: '소개',
      contact: '문의',
      language: '언어',
      english: '영어',
      korean: '한국어',
    },
    about: {
      title: '소개',
      body:
        'Jay Asset Management는 다양한 전략(정적 비중 전략, 모멘텀 기반 라이브 전략 등)을 바탕으로 포트폴리오 자산 배분을 계산하는 웹 앱입니다.',
      disclaimer: '면책: 이 프로젝트는 교육 목적이며 투자 자문이 아닙니다.',
    },
    contact: {
      title: '문의',
      body: '이메일, GitHub, LinkedIn 등 원하는 연락처 정보를 여기에 추가하세요.',
    },
    dashboard: {
      title: '자산 배분 대시보드',
      subtitle: '전략을 선택하고 파라미터를 조정한 뒤 배분 및 모멘텀 차트를 확인하세요.',
      backendConnected: '백엔드 연결됨',
      configure: '설정',
      selectStrategyPrompt: '시작하려면 왼쪽 패널에서 전략을 선택하세요.',
      investmentAmount: '투자 금액',
      amountPlaceholder: '금액을 입력하세요',
      calculate: '계산',
      calculating: '계산 중...',
      reset: '초기화',
      results: '결과',
      runPrompt: '계산을 실행하면 배분 차트와 상세 표를 확인할 수 있습니다.',
      strategy: '전략',
      total: '총액: {currency}{total}',
      missingTickers: '누락 티커: {tickers}',
      allocationChart: '배분 차트',
      momentumChart: '모멘텀 차트',
      defensive: '방어형 {value}%',
      offensive: '공격형 {value}%',
      avg: '평균 {value}%',
      selected: '선택 자산 {value}',
      rebalance: '리밸런싱: {value}',
      errorSelectAmount: '전략을 선택하고 유효한 금액을 입력하세요',
      errorSelectStrategy: '전략을 선택하세요',
    },
    sidebar: {
      strategies: '전략 목록',
      searchPlaceholder: '전략 검색...',
      all: '전체',
      static: '정적',
      live: '실시간',
      noStrategies: '전략이 없습니다.',
    },
    table: {
      title: '배분 표',
      asset: '자산',
      amount: '금액',
      percent: '비중',
      momentum: '모멘텀',
      unknown: '-',
    },
    strategyAbout: {
      about: '소개: {title}',
      rebalance: '리밸런싱: {value}',
    },
    config: {
      strategyParameters: '전략 파라미터',
      paaParameters: 'PAA 파라미터',
      vaaParameters: 'VAA 파라미터',
      etfTickers: 'ETF 티커',
      etfTickersHelp: '쉼표로 구분된 티커 (예: SPY, QQQ, IWM)',
      topN: '상위 ETF 개수',
      topNHelp: '고려할 상위 성과 ETF 수',
      lookbackMonths: '조회 기간(개월)',
      lookbackMonthsHelp: '모멘텀 계산(이동평균)에 사용',
      offensiveAssets: '공격 자산',
      offensiveAssetsHelp: '쉼표로 구분된 티커 (기본값: SPY,EFA,EEM,AGG)',
      defensiveAssets: '방어 자산',
      defensiveAssetsHelp: '쉼표로 구분된 티커 (기본값: LQD,IEF,SHY)',
    },
    chart: {
      allocation: '배분',
      more: '+{count}개 더',
      topMomentum: '상위 {count}개 모멘텀 점수',
    },
    strategies: {
      paa: {
        name: 'PAA (보호 자산 배분)',
        description:
          '모멘텀 순위로 ETF를 선택해 상위 자산에 배분하고, 모멘텀이 약해지면 방어형 채권 비중을 높입니다.',
      },
      vaa: {
        name: 'VAA 공격형 (경계 자산 배분)',
        description:
          '1/3/6/12개월 가중 모멘텀을 사용해 공격/방어 자산 사이를 전환합니다.',
      },
    },
  },
};

translations.en = translations.en || {};
translations.en.navbar = {
  ...(translations.en.navbar || {}),
  dashboard: 'Dashboard',
  learn: 'Learn',
  about: 'About',
  contact: 'Contact',
  menu: 'Open menu',
  language: 'Language',
  english: 'EN',
  korean: 'KO',
};
translations.en.dashboard = {
  ...(translations.en.dashboard || {}),
  title: 'Asset Allocation Dashboard',
  subtitle: 'Choose a strategy, enter an amount, and get allocation results fast.',
  quickActionTitle: 'Quick Action',
  strategySelectLabel: 'Strategy',
  investmentAmount: 'Investment Amount',
  amountPlaceholder: 'Enter amount in $',
  advancedSettings: 'Advanced settings',
  calculate: 'Calculate',
  calculating: 'Calculating...',
  reset: 'Reset',
  results: 'Results',
  runPrompt: 'Run a calculation to see allocation charts and a breakdown table.',
  performanceTitle: 'Historical Performance',
  performanceSubtitle: 'Monthly walk-forward backtest summary',
  performanceUnavailable: 'Performance data is unavailable right now.',
  perfReturn: 'Return {value}',
  perfCagr: 'CAGR {value}',
  perfMaxDrawdown: 'Max DD {value}',
  perfVolatility: 'Volatility {value}',
  perfWinRate: 'Win Rate {value}',
  perfMonthsTested: 'Months {value}',
  perfWindow: 'Window {start} to {end}',
  perfMissingTickers: 'Performance missing tickers: {tickers}',
};
translations.en.learn = {
  title: 'Learn',
  subtitle: 'Follow this guided tutorial to understand exactly how to use the dashboard.',
  progressTitle: 'Tutorial Progress',
  progressCount: '{done} of {total} completed',
  stepLabel: 'Step {current} of {total}',
  completedTag: 'Completed',
  sections: {
    whatThisDoes: 'What this step does',
    whatToClick: 'What to click',
    expectedResult: 'What result you should see',
    commonMistake: 'Common mistake',
  },
  actions: {
    startTutorial: 'Start Tutorial',
    jumpDashboard: 'Jump to Dashboard',
    tryOnDashboard: 'Try this on Dashboard',
    markComplete: 'Mark as complete',
    back: 'Back',
    next: 'Next',
    finish: 'Finish',
  },
  steps: {
    chooseStrategy: {
      title: 'Choose a strategy',
      whatThisDoes: [
        'This defines how assets are selected and weighted.',
        'PAA tends to be balanced with defense, while VAA is usually more aggressive.',
      ],
      whatToClick: [
        'Open the Strategy dropdown in Quick Action.',
        'Pick PAA first for a safer beginner start.',
      ],
      expectedResult: [
        'You should see strategy description and rebalance frequency.',
        'Advanced settings will match the selected strategy.',
      ],
      commonMistake: 'Changing strategy after entering many parameters without recalculating.',
    },
    enterAmount: {
      title: 'Enter investment amount',
      whatThisDoes: [
        'This sets the total money used for allocation amounts.',
        'Percentages stay strategy-driven; dollar amounts scale from this value.',
      ],
      whatToClick: [
        'Type your amount in the Investment Amount field.',
        'Use a realistic test amount like 10000 for first practice.',
      ],
      expectedResult: [
        'No calculation runs yet; amount is stored until you press Calculate.',
        'If amount is empty or 0, an error will show on calculate.',
      ],
      commonMistake: 'Using commas or symbols in a format the browser field does not accept.',
    },
    runCalculation: {
      title: 'Run calculation',
      whatThisDoes: [
        'Runs strategy logic and generates an allocation plan.',
        'If cache is active, repeat inputs may return faster.',
      ],
      whatToClick: [
        'Press the Calculate button in Quick Action.',
      ],
      expectedResult: [
        'Results panel shows allocation chart and allocation table.',
        'Dynamic strategies also show momentum/performance metadata.',
      ],
      commonMistake: 'Forgetting to press Calculate after changing strategy or amount.',
    },
    readAllocation: {
      title: 'Read allocation output',
      whatThisDoes: [
        'Shows where your money is distributed across tickers.',
        'Chart gives quick visual split, table gives exact numbers.',
      ],
      whatToClick: [
        'Check Allocation Chart first for high-level split.',
        'Then verify exact dollar and percent values in Allocation Table.',
      ],
      expectedResult: [
        'Total percentages should sum to about 100%.',
        'Each row should show asset, amount, weight, and momentum if available.',
      ],
      commonMistake: 'Reading only percentages and ignoring actual dollar size per asset.',
    },
    readPerformance: {
      title: 'Understand historical performance',
      whatThisDoes: [
        'Shows backtested behavior summary, not future guarantee.',
        'Helps compare risk/return profile across strategies.',
      ],
      whatToClick: [
        'Look at Return, CAGR, Max Drawdown, Volatility, and Win Rate chips.',
        'Use this as context, not prediction.',
      ],
      expectedResult: [
        'Metrics appear for dynamic strategies when data is available.',
        'If unavailable, a warning message explains the issue.',
      ],
      commonMistake: 'Treating historical CAGR as guaranteed future annual return.',
    },
    resetAndAdvanced: {
      title: 'Use reset and advanced settings correctly',
      whatThisDoes: [
        'Reset clears results and restores default parameters for current strategy.',
        'Advanced settings lets you tune ticker lists and lookback inputs.',
      ],
      whatToClick: [
        'Press Reset to start a fresh run with same strategy defaults.',
        'Open Advanced settings only when you need customization.',
      ],
      expectedResult: [
        'Strategy remains selected after reset.',
        'Results disappear until you calculate again.',
      ],
      commonMistake: 'Expecting Reset to keep old custom parameters after a full clear.',
    },
  },
  references: {
    title: 'Beginner References',
    paaVaaTitle: 'PAA vs VAA at a glance',
    paaVaaBody:
      'PAA generally diversifies and adds defense as momentum weakens. VAA rotates to strongest offensive asset or defensive asset when risk-off.',
    metricsTitle: 'How to read key metrics',
    metricsBody:
      'CAGR is annualized return in the tested window. Max drawdown is the worst historical decline. Volatility reflects return variability.',
    troubleshootingTitle: 'Common troubleshooting',
    troubleshootingBody:
      'If metrics are missing, check backend data availability and strategy inputs. If response is slow, verify API/data provider health.',
    faqTitle: 'Important reminder',
    faqBody:
      'This tool is educational. Always verify assumptions, rebalance discipline, and risk tolerance before real investing.',
  },
};
translations.en.ticker = {
  moreInfo: 'More ticker info',
  assetType: 'Asset type: {value}',
  market: 'Market: {value}',
  role: 'Role: {value}',
};
translations.en.table = {
  ...(translations.en.table || {}),
  tickerHint: 'Hover or tap a ticker symbol to see what it represents.',
};

translations.ko = translations.ko || {};
translations.ko.navbar = {
  ...(translations.ko.navbar || {}),
  dashboard: '\uB300\uC2DC\uBCF4\uB4DC',
  learn: '\uD559\uC2B5',
  about: '\uC18C\uAC1C',
  contact: '\uBB38\uC758',
  menu: '\uBA54\uB274 \uC5F4\uAE30',
  language: '\uC5B8\uC5B4',
  english: '\uC601\uC5B4',
  korean: '\uD55C\uAD6D\uC5B4',
};
translations.ko.dashboard = {
  ...(translations.ko.dashboard || {}),
  title: '\uC790\uC0B0 \uBC30\uBD84 \uB300\uC2DC\uBCF4\uB4DC',
  subtitle: '\uC804\uB7B5\uC744 \uACE0\uB974\uACE0 \uAE08\uC561\uC744 \uC785\uB825\uD55C \uB4A4, \uBC14\uB85C \uBC30\uBD84 \uACB0\uACFC\uB97C \uD655\uC778\uD558\uC138\uC694.',
  quickActionTitle: '\uBE60\uB978 \uC2E4\uD589',
  strategySelectLabel: '\uC804\uB7B5',
  investmentAmount: '\uD22C\uC790 \uAE08\uC561',
  amountPlaceholder: '\uAE08\uC561\uC744 \uC785\uB825\uD558\uC138\uC694',
  advancedSettings: '\uACE0\uAE09 \uC124\uC815',
  calculate: '\uACC4\uC0B0',
  calculating: '\uACC4\uC0B0 \uC911...',
  reset: '\uCD08\uAE30\uD654',
  results: '\uACB0\uACFC',
  runPrompt: '\uACC4\uC0B0\uC744 \uC2E4\uD589\uD558\uBA74 \uBC30\uBD84 \uCC28\uD2B8\uC640 \uD14C\uC774\uBE14\uC744 \uD655\uC778\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
  performanceTitle: '\uACFC\uAC70 \uC131\uACFC',
  performanceSubtitle: '\uC6D4\uBCC4 \uC6CC\uD06C\uD3EC\uC6CC\uB4DC \uBC31\uD14C\uC2A4\uD2B8 \uC694\uC57D',
  performanceUnavailable: '\uD604\uC7AC \uC131\uACFC \uB370\uC774\uD130\uB97C \uBD88\uB7EC\uC62C \uC218 \uC5C6\uC2B5\uB2C8\uB2E4.',
  perfReturn: '\uC218\uC775\uB960 {value}',
  perfCagr: '\uC5F0\uBCF5\uB9AC {value}',
  perfMaxDrawdown: '\uCD5C\uB300 \uB099\uD3ED {value}',
  perfVolatility: '\uBCC0\uB3D9\uC131 {value}',
  perfWinRate: '\uC6D4 \uC2B9\uB960 {value}',
  perfMonthsTested: '\uD14C\uC2A4\uD2B8 \uAE30\uAC04 {value}\uAC1C\uC6D4',
  perfWindow: '\uAE30\uAC04 {start} ~ {end}',
  perfMissingTickers: '\uC131\uACFC \uACC4\uC0B0 \uB204\uB77D \uD2F0\uCEE4: {tickers}',
};
translations.ko.learn = {
  ...translations.en.learn,
  title: '\uD559\uC2B5',
  subtitle: '\uB300\uC2DC\uBCF4\uB4DC \uC0AC\uC6A9 \uBC95\uC744 \uB2E8\uACC4\uBCC4 \uD29C\uD1A0\uB9AC\uC5BC\uB85C \uC775\uD788\uC138\uC694.',
  progressTitle: '\uD29C\uD1A0\uB9AC\uC5BC \uC9C4\uD589\uB3C4',
  progressCount: '{done} / {total} \uC644\uB8CC',
  stepLabel: '{total}\uB2E8\uACC4 \uC911 {current}\uB2E8\uACC4',
  completedTag: '\uC644\uB8CC',
  sections: {
    whatThisDoes: '\uC774 \uB2E8\uACC4\uC758 \uBAA9\uC801',
    whatToClick: '\uD074\uB9AD\uD560 \uAC83',
    expectedResult: '\uD655\uC778\uD560 \uACB0\uACFC',
    commonMistake: '\uC790\uC8FC \uD558\uB294 \uC2E4\uC218',
  },
  actions: {
    startTutorial: '\uD29C\uD1A0\uB9AC\uC5BC \uC2DC\uC791',
    jumpDashboard: '\uB300\uC2DC\uBCF4\uB4DC\uB85C \uC774\uB3D9',
    tryOnDashboard: '\uB300\uC2DC\uBCF4\uB4DC\uC5D0\uC11C \uC2E4\uD589',
    markComplete: '\uD604\uC7AC \uB2E8\uACC4 \uC644\uB8CC',
    back: '\uC774\uC804',
    next: '\uB2E4\uC74C',
    finish: '\uB9C8\uCE58\uAE30',
  },
  references: {
    title: '\uCD08\uBCF4\uC790 \uCC38\uACE0 \uAC00\uC774\uB4DC',
    paaVaaTitle: 'PAA / VAA \uBE60\uB978 \uBE44\uAD50',
    paaVaaBody:
      'PAA\uB294 \uBD84\uC0B0\uC640 \uBC29\uC5B4 \uBE44\uC911 \uC870\uC808\uC5D0 \uAC15\uC810\uC774 \uC788\uACE0, VAA\uB294 \uC0C1\uD669\uC5D0 \uB530\uB77C \uB354 \uACF5\uACA9\uC801\uC73C\uB85C \uC790\uC0B0\uC744 \uD68C\uC804\uD569\uB2C8\uB2E4.',
    metricsTitle: '\uD575\uC2EC \uC9C0\uD45C \uD574\uC11D',
    metricsBody:
      'CAGR\uB294 \uD14C\uC2A4\uD2B8 \uAE30\uAC04 \uAE30\uC900 \uC5F0\uBCF5\uB9AC \uC218\uC775\uB960\uC774\uACE0, \uCD5C\uB300 \uB099\uD3ED\uC740 \uACFC\uAC70 \uCD5C\uB300 \uD558\uB77D \uD3ED\uC744 \uB73B\uD569\uB2C8\uB2E4.',
    troubleshootingTitle: '\uC790\uC8FC \uBC1C\uC0DD\uD558\uB294 \uBB38\uC81C',
    troubleshootingBody:
      '\uACB0\uACFC\uAC00 \uC548 \uB098\uC624\uBA74 \uC785\uB825 \uAC12, \uB370\uC774\uD130 \uC18C\uC2A4 \uC0C1\uD0DC, \uBC31\uC5D4\uB4DC \uC5F0\uACB0 \uC5EC\uBD80\uB97C \uBA3C\uC800 \uD655\uC778\uD558\uC138\uC694.',
    faqTitle: '\uC911\uC694 \uC548\uB0B4',
    faqBody:
      '\uBCF8 \uC571\uC740 \uAD50\uC721\uC6A9 \uB3C4\uAD6C\uC785\uB2C8\uB2E4. \uC2E4\uC81C \uD22C\uC790 \uC804\uC5D0 \uBC18\uB4DC\uC2DC \uB9AC\uC2A4\uD06C\uC640 \uC790\uC2E0\uC758 \uC6D0\uCE59\uC744 \uC810\uAC80\uD558\uC138\uC694.',
  },
};
translations.ko.learn.steps = {
  chooseStrategy: {
    title: '\uC804\uB7B5 \uC120\uD0DD\uD558\uAE30',
    whatThisDoes: [
      '\uC790\uC0B0\uC744 \uC5B4\uB5BB\uAC8C \uC120\uD0DD\uD558\uACE0 \uBE44\uC911\uC744 \uB098\uB20C\uC9C0 \uACB0\uC815\uD569\uB2C8\uB2E4.',
      'PAA\uB294 \uBC29\uC5B4\uB97C \uD3EC\uD568\uD55C \uADE0\uD615\uD615\uC5D0 \uAC00\uAE5D\uACE0, VAA\uB294 \uBCF4\uD1B5 \uB354 \uACF5\uACA9\uC801\uC785\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uBE60\uB978 \uC2E4\uD589 \uC601\uC5ED\uC5D0\uC11C \uC804\uB7B5 \uB4DC\uB86D\uB2E4\uC6B4\uC744 \uC5EC\uC138\uC694.',
      '\uCD08\uBCF4\uB77C\uBA74 \uBA3C\uC800 PAA\uB85C \uC2DC\uC791\uD558\uC138\uC694.',
    ],
    expectedResult: [
      '\uC804\uB7B5 \uC124\uBA85\uACFC \uB9AC\uBC38\uB7F0\uC2F1 \uC8FC\uAE30\uAC00 \uD45C\uC2DC\uB429\uB2C8\uB2E4.',
      '\uACE0\uAE09 \uC124\uC815\uC774 \uC120\uD0DD\uD55C \uC804\uB7B5\uC5D0 \uB9DE\uAC8C \uBC14\uB00C\uB2C8\uB2E4.',
    ],
    commonMistake: '\uD30C\uB77C\uBBF8\uD130\uB97C \uB9CE\uC774 \uBC14\uAFBC \uB4A4 \uACC4\uC0B0 \uBC84\uD2BC\uC744 \uB2E4\uC2DC \uB204\uB974\uC9C0 \uC54A\uB294 \uACBD\uC6B0.',
  },
  enterAmount: {
    title: '\uD22C\uC790 \uAE08\uC561 \uC785\uB825\uD558\uAE30',
    whatThisDoes: [
      '\uBC30\uBD84 \uACC4\uC0B0\uC5D0 \uC0AC\uC6A9\uB420 \uCD1D \uD22C\uC790\uAE08\uC744 \uC124\uC815\uD569\uB2C8\uB2E4.',
      '\uBE44\uC911\uC740 \uC804\uB7B5\uC774 \uACB0\uC815\uD558\uACE0, \uAE08\uC561\uC740 \uC785\uB825\uD55C \uCD1D\uC561\uC5D0 \uBE44\uB840\uD574 \uACC4\uC0B0\uB429\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uD22C\uC790 \uAE08\uC561 \uC785\uB825\uCE78\uC5D0 \uC6D0\uD558\uB294 \uC218\uCE58\uB97C \uC785\uB825\uD558\uC138\uC694.',
      '\uCC98\uC74C\uC5D0\uB294 10000 \uAC19\uC740 \uD14C\uC2A4\uD2B8 \uAE08\uC561\uC73C\uB85C \uC5F0\uC2B5\uD558\uC138\uC694.',
    ],
    expectedResult: [
      '\uC785\uB825\uD55C \uAE08\uC561\uC740 \uC800\uC7A5\uB418\uC9C0\uB9CC, \uACC4\uC0B0 \uBC84\uD2BC\uC744 \uB204\uB974\uAE30 \uC804\uAE4C\uC9C0 \uACB0\uACFC\uB294 \uBCC0\uD558\uC9C0 \uC54A\uC2B5\uB2C8\uB2E4.',
      '\uAE08\uC561\uC774 \uBE44\uC5B4 \uC788\uAC70\uB098 0\uC774\uBA74 \uACC4\uC0B0 \uC2DC \uC624\uB958 \uBA54\uC2DC\uC9C0\uAC00 \uD45C\uC2DC\uB429\uB2C8\uB2E4.',
    ],
    commonMistake: '\uBE0C\uB77C\uC6B0\uC800 \uC22B\uC790 \uD615\uC2DD\uC5D0 \uB9DE\uC9C0 \uC54A\uB294 \uAE30\uD638\uB97C \uD568\uAED8 \uC785\uB825\uD558\uB294 \uACBD\uC6B0.',
  },
  runCalculation: {
    title: '\uACC4\uC0B0 \uC2E4\uD589\uD558\uAE30',
    whatThisDoes: [
      '\uC120\uD0DD\uD55C \uC804\uB7B5 \uB85C\uC9C1\uC744 \uC2E4\uD589\uD574 \uC790\uC0B0 \uBC30\uBD84 \uACB0\uACFC\uB97C \uB9CC\uB4ED\uB2C8\uB2E4.',
      '\uCE90\uC2DC\uAC00 \uD65C\uC131\uD654\uB418\uC5C8\uB2E4\uBA74 \uAC19\uC740 \uC785\uB825 \uC870\uD569\uC740 \uB354 \uBE60\uB974\uAC8C \uBC18\uD658\uB420 \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uBE60\uB978 \uC2E4\uD589 \uC601\uC5ED\uC758 \uACC4\uC0B0 \uBC84\uD2BC\uC744 \uB204\uB974\uC138\uC694.',
    ],
    expectedResult: [
      '\uACB0\uACFC \uD328\uB110\uC5D0 \uBC30\uBD84 \uCC28\uD2B8\uC640 \uBC30\uBD84 \uD14C\uC774\uBE14\uC774 \uB098\uD0C0\uB0A9\uB2C8\uB2E4.',
      '\uB3D9\uC801 \uC804\uB7B5\uC740 \uBAA8\uBA58\uD140/\uC131\uACFC \uAD00\uB828 \uC815\uBCF4\uB3C4 \uD568\uAED8 \uBCF4\uC5EC\uC90D\uB2C8\uB2E4.',
    ],
    commonMistake: '\uC804\uB7B5\uC774\uB098 \uAE08\uC561\uC744 \uBC14\uAFBE \uD6C4 \uACC4\uC0B0\uC744 \uB2E4\uC2DC \uB204\uB974\uC9C0 \uC54A\uB294 \uAC83.',
  },
  readAllocation: {
    title: '\uBC30\uBD84 \uACB0\uACFC \uC77D\uAE30',
    whatThisDoes: [
      '\uD604\uC7AC \uD22C\uC790\uAE08\uC774 \uAC01 \uD2F0\uCEE4\uC5D0 \uC5BC\uB9C8\uB098 \uBC30\uBD84\uB418\uB294\uC9C0 \uD655\uC778\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
      '\uCC28\uD2B8\uB294 \uC804\uCCB4 \uAD6C\uC870\uB97C \uBE60\uB974\uAC8C, \uD14C\uC774\uBE14\uC740 \uC815\uD655\uD55C \uC218\uCE58\uB97C \uBCF4\uC5EC\uC90D\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uBA3C\uC800 \uBC30\uBD84 \uCC28\uD2B8\uB97C \uBCF4\uACE0 \uD070 \uD750\uB984\uC744 \uD30C\uC545\uD558\uC138\uC694.',
      '\uB2E4\uC74C\uC73C\uB85C \uBC30\uBD84 \uD14C\uC774\uBE14\uC5D0\uC11C \uAE08\uC561\uACFC \uBE44\uC911\uC744 \uD655\uC778\uD558\uC138\uC694.',
    ],
    expectedResult: [
      '\uC804\uCCB4 \uBE44\uC911 \uD569\uACC4\uAC00 \uC57D 100%\uC5D0 \uAC00\uAE5D\uAC8C \uB098\uC640\uC57C \uD569\uB2C8\uB2E4.',
      '\uAC01 \uD589\uC5D0\uC11C \uC790\uC0B0, \uAE08\uC561, \uBE44\uC911, (\uAC00\uB2A5\uD55C \uACBD\uC6B0) \uBAA8\uBA58\uD140\uC744 \uBCFC \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
    ],
    commonMistake: '\uBE44\uC911\uB9CC \uBCF4\uACE0 \uC2E4\uC81C \uAE08\uC561 \uADDC\uBAA8\uB97C \uD655\uC778\uD558\uC9C0 \uC54A\uB294 \uAC83.',
  },
  readPerformance: {
    title: '\uACFC\uAC70 \uC131\uACFC \uD574\uC11D\uD558\uAE30',
    whatThisDoes: [
      '\uC804\uB7B5\uC758 \uACFC\uAC70 \uD14C\uC2A4\uD2B8 \uC131\uACFC\uB97C \uC694\uC57D\uD574 \uBCF4\uC5EC\uC90D\uB2C8\uB2E4.',
      '\uBBF8\uB798 \uC218\uC775 \uBCF4\uC7A5\uC774 \uC544\uB2C8\uB77C \uC804\uB7B5 \uD2B9\uC131 \uD30C\uC545\uC6A9 \uC9C0\uD45C\uC785\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uC218\uC775\uB960, CAGR, \uCD5C\uB300 \uB099\uD3ED, \uBCC0\uB3D9\uC131, \uC6D4 \uC2B9\uB960 \uCE69\uC744 \uCC28\uB840\uB85C \uD655\uC778\uD558\uC138\uC694.',
      '\uC9C0\uD45C\uB294 \uC608\uCE21\uC774 \uC544\uB2C8\uB77C \uBE44\uAD50 \uAE30\uC900\uC73C\uB85C \uC0AC\uC6A9\uD558\uC138\uC694.',
    ],
    expectedResult: [
      '\uB3D9\uC801 \uC804\uB7B5\uC5D0\uC11C \uB370\uC774\uD130\uAC00 \uC788\uC73C\uBA74 \uC131\uACFC \uC9C0\uD45C\uAC00 \uD45C\uC2DC\uB429\uB2C8\uB2E4.',
      '\uB370\uC774\uD130\uAC00 \uC5C6\uC73C\uBA74 \uC0AC\uC720\uAC00 \uD3EC\uD568\uB41C \uACBD\uACE0 \uBA54\uC2DC\uC9C0\uAC00 \uB098\uD0C0\uB0A9\uB2C8\uB2E4.',
    ],
    commonMistake: '\uACFC\uAC70 CAGR\uC744 \uBBF8\uB798 \uD655\uC815 \uC218\uC775\uB960\uB85C \uD574\uC11D\uD558\uB294 \uAC83.',
  },
  resetAndAdvanced: {
    title: '\uCD08\uAE30\uD654\uC640 \uACE0\uAE09 \uC124\uC815 \uC0AC\uC6A9\uD558\uAE30',
    whatThisDoes: [
      '\uCD08\uAE30\uD654\uB294 \uD604\uC7AC \uC804\uB7B5\uC744 \uC720\uC9C0\uD55C \uCC44 \uACB0\uACFC\uB97C \uC9C0\uC6B0\uACE0 \uAE30\uBCF8\uAC12\uC73C\uB85C \uB3CC\uB9BD\uB2C8\uB2E4.',
      '\uACE0\uAE09 \uC124\uC815\uC5D0\uC11C \uD2F0\uCEE4 \uBAA9\uB85D\uACFC \uCC3E\uAE30 \uAE30\uAC04 \uB4F1\uC744 \uC870\uC815\uD560 \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
    ],
    whatToClick: [
      '\uB2E4\uC2DC \uC2DC\uC791\uD560 \uB54C \uCD08\uAE30\uD654 \uBC84\uD2BC\uC744 \uB204\uB974\uC138\uC694.',
      '\uD544\uC694\uD560 \uB54C\uB9CC \uACE0\uAE09 \uC124\uC815 \uC544\uCF54\uB514\uC5B8\uC744 \uC5F4\uC5B4 \uD30C\uB77C\uBBF8\uD130\uB97C \uBC14\uAFB8\uC138\uC694.',
    ],
    expectedResult: [
      '\uCD08\uAE30\uD654 \uD6C4\uC5D0\uB3C4 \uC120\uD0DD \uC804\uB7B5\uC740 \uADF8\uB300\uB85C \uC720\uC9C0\uB429\uB2C8\uB2E4.',
      '\uB2E4\uC2DC \uACC4\uC0B0\uD558\uAE30 \uC804\uAE4C\uC9C0 \uACB0\uACFC \uD328\uB110\uC740 \uBE44\uC5B4 \uC788\uC2B5\uB2C8\uB2E4.',
    ],
    commonMistake: '\uCD08\uAE30\uD654 \uD6C4\uC5D0 \uC608\uC804 \uC0AC\uC6A9\uC790 \uC9C0\uC815 \uAC12\uC774 \uADF8\uB300\uB85C \uB0A8\uC544\uC788\uC744 \uAC83\uC73C\uB85C \uAE30\uB300\uD558\uB294 \uAC83.',
  },
};
translations.ko.ticker = {
  moreInfo: '\uD2F0\uCEE4 \uC815\uBCF4 \uBCF4\uAE30',
  assetType: '\uC790\uC0B0 \uC720\uD615: {value}',
  market: '\uC2DC\uC7A5: {value}',
  role: '\uC5ED\uD560: {value}',
};
translations.ko.table = {
  ...(translations.ko.table || {}),
  tickerHint: '\uD2F0\uCEE4 \uC2EC\uBCFC\uC5D0 \uB9C8\uC6B0\uC2A4 \uC624\uBC84\uB97C \uD558\uAC70\uB098 \uD0ED\uD558\uBA74 \uC790\uC0B0 \uC124\uBA85\uC744 \uBCFC \uC218 \uC788\uC2B5\uB2C8\uB2E4.',
};
