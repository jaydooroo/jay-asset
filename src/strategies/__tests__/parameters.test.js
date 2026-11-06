import { buildStrategyParameters } from '../registry';
import { parseCommaTickers, parseNumber } from '../utils';

describe('parseCommaTickers', () => {
  it('trims, uppercases and drops blanks', () => {
    expect(parseCommaTickers(' spy, qqq ,,IEF ')).toEqual(['SPY', 'QQQ', 'IEF']);
  });

  it('handles empty input', () => {
    expect(parseCommaTickers(undefined)).toEqual([]);
    expect(parseCommaTickers('')).toEqual([]);
  });
});

describe('parseNumber', () => {
  it('parses numbers and rejects text', () => {
    expect(parseNumber('6')).toBe(6);
    expect(parseNumber('7.5')).toBe(7.5);
    expect(parseNumber('abc')).toBeNull();
    expect(parseNumber('')).toBeNull();
  });
});

describe('buildStrategyParameters', () => {
  it('sends PAA tickers as a list and numbers as numbers', () => {
    expect(buildStrategyParameters('paa', [], { etfs: 'spy,qqq', top_n: '3', lookback_months: '12' })).toEqual({
      etfs: ['SPY', 'QQQ'],
      top_n: 3,
      lookback_months: 12,
    });
  });

  it('leaves out empty PAA fields so the backend uses its defaults', () => {
    expect(buildStrategyParameters('paa', [], { etfs: '', top_n: '' })).toEqual({});
  });

  it('builds VAA ticker lists', () => {
    expect(buildStrategyParameters('vaa', [], { offensive_assets: 'spy, efa', defensive_assets: 'shy' })).toEqual({
      offensive_assets: ['SPY', 'EFA'],
      defensive_assets: ['SHY'],
    });
  });

  it('follows the backend schema for every other strategy', () => {
    const defs = [
      { name: 'risk_assets', type: 'text' },
      { name: 'sma_months', type: 'number' },
      { name: 'weights', type: 'text' },
    ];
    expect(
      buildStrategyParameters('gtaa', defs, { risk_assets: 'spy,efa', sma_months: '10', weights: 'SPY:60,AGG:40' }),
    ).toEqual({ risk_assets: ['SPY', 'EFA'], sma_months: 10, weights: 'SPY:60,AGG:40' });
  });

  it('skips blank and invalid generic values', () => {
    const defs = [
      { name: 'sma_months', type: 'number' },
      { name: 'weights', type: 'text' },
      { name: 'canary_assets', type: 'text' },
    ];
    expect(buildStrategyParameters('gtaa', defs, { sma_months: 'x', weights: '', canary_assets: ' , ' })).toEqual({});
  });
});
