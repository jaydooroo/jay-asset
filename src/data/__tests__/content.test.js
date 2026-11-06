import { getTickerMetadata } from '../tickerMetadata';
import { strategyEducation, strategyEducationKo } from '../strategyEducation';
import { translations } from '../../i18n/translations';

// Which strategies exist is checked against the backend registry in
// backend/tests/test_strategy_contracts.py; these tests keep the two
// languages in step with each other.

describe('getTickerMetadata', () => {
  it('returns known ticker details', () => {
    expect(getTickerMetadata('spy')).toMatchObject({ ticker: 'SPY', name: 'SPDR S&P 500 ETF Trust' });
  });

  it('falls back for unknown tickers', () => {
    expect(getTickerMetadata('zzz')).toEqual({
      ticker: 'ZZZ',
      name: 'ZZZ',
      assetType: 'ETF',
      market: 'Global',
      role: 'N/A',
    });
  });
});

describe('Korean and English content match', () => {
  it('has English education text for every Korean entry', () => {
    // English also keeps a few retired entries (conservative, balanced, ...).
    Object.keys(strategyEducationKo).forEach((id) => {
      expect(strategyEducation[id]).toBeDefined();
      expect(strategyEducationKo[id].sections.length).toBe(strategyEducation[id].sections.length);
    });
  });

  it('has strategy names and descriptions for the same strategies', () => {
    const en = translations.en.strategies;
    const ko = translations.ko.strategies;
    expect(Object.keys(ko).sort()).toEqual(Object.keys(en).sort());
    Object.keys(en).forEach((id) => {
      expect(ko[id].name).toBeTruthy();
      expect(ko[id].description).toBeTruthy();
    });
  });

  it('has the same translation keys everywhere', () => {
    const keyPaths = (obj, prefix = '') =>
      Object.entries(obj).flatMap(([key, value]) =>
        value && typeof value === 'object' && !Array.isArray(value)
          ? keyPaths(value, `${prefix}${key}.`)
          : [`${prefix}${key}`],
      );
    expect(keyPaths(translations.ko).sort()).toEqual(keyPaths(translations.en).sort());
  });
});
