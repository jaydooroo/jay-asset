import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';
import ApiService from '../../services/api';
import { LanguageProvider } from '../../i18n/LanguageContext';

jest.mock('../../services/api');

const PAA = {
  name: 'PAA',
  description: 'Protective asset allocation',
  category: 'tactical',
  parameters: [
    { name: 'etfs', label: 'ETFs', type: 'text', default: 'SPY,QQQ,IEF' },
    { name: 'top_n', label: 'Top N', type: 'number', default: 2 },
    { name: 'lookback_months', label: 'Lookback', type: 'number', default: 12 },
  ],
};

beforeEach(() => {
  localStorage.setItem('jay-asset-language', 'en');
  ApiService.getStrategies.mockResolvedValue({ paa: PAA });
  ApiService.getPerformance.mockResolvedValue({ strategy_id: 'paa', metrics: {} });
  ApiService.calculateAllocation.mockResolvedValue({
    allocation: { SPY: 6000, QQQ: 4000 },
    allocation_weights: { SPY: 0.6, QQQ: 0.4 },
    date: '2026-11-24',
  });
});

afterEach(() => jest.resetAllMocks());

test('shows a result for the example amount without a click', async () => {
  render(<LanguageProvider><Dashboard /></LanguageProvider>);

  await waitFor(() => expect(ApiService.calculateAllocation).toHaveBeenCalledTimes(1));
  expect(ApiService.calculateAllocation).toHaveBeenCalledWith(
    'paa', 10000, { etfs: ['SPY', 'QQQ', 'IEF'], top_n: 2, lookback_months: 12 });
  expect(await screen.findByText(/\$10,000/)).toBeInTheDocument();
  expect(screen.queryByText(/Run a calculation/)).not.toBeInTheDocument();
  expect(ApiService.healthCheck).not.toHaveBeenCalled();
});

test('calculates only after the performance request finishes', async () => {
  // Overlapping requests would start a second, cold Lambda instance.
  let finishPerformance;
  ApiService.getPerformance.mockReturnValue(new Promise((resolve) => { finishPerformance = resolve; }));
  render(<LanguageProvider><Dashboard /></LanguageProvider>);

  await waitFor(() => expect(ApiService.getPerformance).toHaveBeenCalled());
  expect(ApiService.calculateAllocation).not.toHaveBeenCalled();

  finishPerformance({ strategy_id: 'paa', metrics: {} });
  await waitFor(() => expect(ApiService.calculateAllocation).toHaveBeenCalledTimes(1));
});

test('a failed calculation is shown and not retried in a loop', async () => {
  ApiService.calculateAllocation.mockRejectedValue(new Error('No price data available'));
  render(<LanguageProvider><Dashboard /></LanguageProvider>);

  expect(await screen.findByText('No price data available')).toBeInTheDocument();
  await new Promise((resolve) => setTimeout(resolve, 50));
  expect(ApiService.calculateAllocation).toHaveBeenCalledTimes(1);
});
