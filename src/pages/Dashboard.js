import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Container,
  Paper,
  TextField,
  Typography,
  CircularProgress,
  Divider,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';

import ApiService from '../services/api';
import StrategyAboutPanel from '../components/StrategyAboutPanel';
import AllocationDonutChart from '../components/dashboard/AllocationDonutChart';
import MomentumBarChart from '../components/dashboard/MomentumBarChart';
import ResultsTable from '../components/dashboard/ResultsTable';
import StrategySidebar from '../components/dashboard/StrategySidebar';
import { staticStrategies } from '../data/staticStrategies';
import { strategyEducation } from '../data/strategyEducation';
import { buildStrategyParameters, getStrategyConfigPanel } from '../strategies/registry';
import './Dashboard.css';

const Dashboard = () => {
  const [strategies, setStrategies] = useState(staticStrategies);
  const [selectedStrategyId, setSelectedStrategyId] = useState('');
  const [amount, setAmount] = useState('');
  const [paramValues, setParamValues] = useState({});

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendAvailable, setBackendAvailable] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        await ApiService.healthCheck();
        setBackendAvailable(true);

        const dynamic = await ApiService.getStrategies();
        const merged = { ...staticStrategies };
        Object.keys(dynamic).forEach((key) => {
          merged[key] = { ...dynamic[key], type: 'dynamic' };
        });
        setStrategies(merged);
      } catch {
        setBackendAvailable(false);
      }
    };
    load();
  }, []);

  const selectedStrategy = selectedStrategyId ? strategies[selectedStrategyId] : null;
  const selectedEducation = selectedStrategyId ? strategyEducation[selectedStrategyId] : null;

  const handleSelectStrategy = (id) => {
    setSelectedStrategyId(id);
    setResults(null);
    setError(null);

    const next = strategies[id];
    if (next && next.parameters && next.parameters.length > 0) {
      const defaults = {};
      next.parameters.forEach((param) => {
        defaults[param.name] = param.default ?? '';
      });
      setParamValues(defaults);
    } else {
      setParamValues({});
    }
  };

  const handleParamChange = (name, value) => {
    setParamValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setAmount('');
    setResults(null);
    setError(null);
    setParamValues({});
    setSelectedStrategyId('');
  };

  const handleCalculate = async () => {
    if (!selectedStrategyId || !amount || Number(amount) <= 0) {
      setError('Please select a strategy and enter a valid amount');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const totalAmount = Number.parseFloat(amount);
      const strategy = strategies[selectedStrategyId];

      if (!strategy) {
        setError('Please select a strategy');
        return;
      }

      if (strategy.type === 'static') {
        const breakdown = Object.entries(strategy.allocation).map(([asset, percentage]) => ({
          asset,
          percentage: Number(percentage),
          amount: Number(((totalAmount * percentage) / 100).toFixed(2)),
        }));

        setResults({
          strategy: strategy.name,
          description: strategy.description,
          totalAmount,
          breakdown,
          type: 'static',
        });
        return;
      }

      // Dynamic strategy: let the strategy-specific frontend code decide how to parse params.
      const parameters = buildStrategyParameters(selectedStrategyId, strategy.parameters, paramValues);

      const result = await ApiService.calculateAllocation(selectedStrategyId, totalAmount, parameters);

      const breakdown = Object.entries(result.allocation).map(([asset, amt]) => ({
        asset,
        amount: Number(amt),
        percentage: (Number(amt) / totalAmount) * 100,
      }));

      if (result.momentum_scores) {
        const scores = result.momentum_scores;
        breakdown.sort((a, b) => (scores[b.asset] ?? Number.NEGATIVE_INFINITY) - (scores[a.asset] ?? Number.NEGATIVE_INFINITY));
      } else {
        breakdown.sort((a, b) => b.percentage - a.percentage);
      }

      setResults({
        strategy: result.strategy,
        description: strategy.description,
        totalAmount,
        breakdown,
        type: 'dynamic',
        metadata: {
          date: result.date,
          defensive_ratio: result.defensive_ratio,
          offensive_ratio: result.offensive_ratio,
          momentum_scores: result.momentum_scores,
          avg_momentum: result.avg_momentum,
          best_etf: result.best_etf,
          worst_etf: result.worst_etf,
          selected_asset: result.selected_asset,
          mode: result.mode,
          missing_tickers: result.missing_tickers,
        },
      });
    } catch (err) {
      setError(err.message || 'Failed to calculate allocation');
    } finally {
      setLoading(false);
    }
  };

  const donutData = useMemo(() => {
    if (!results?.breakdown) return [];
    return results.breakdown.map((row) => ({
      label: row.asset,
      value: Number(row.percentage ?? ((Number(row.amount) / results.totalAmount) * 100)),
    }));
  }, [results]);

  const momentumScores = results?.metadata?.momentum_scores;
  const ConfigPanel = useMemo(() => getStrategyConfigPanel(selectedStrategyId), [selectedStrategyId]);

  return (
    <div className="dashboard-root">
      <Container maxWidth="xl">
        <Paper elevation={0} sx={{ p: 2, mb: 2, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.9)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUpIcon sx={{ fontSize: 34 }} />
            <Box sx={{ flex: 1 }}>
              <Typography variant="h5" sx={{ fontWeight: 900 }}>
                Asset Allocation Dashboard
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pick a strategy, tune parameters, and view allocation + momentum charts.
              </Typography>
            </Box>
            {backendAvailable && <Chip label="Backend Connected" color="success" size="small" />}
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box className="dashboard-grid-wrap">
          <Box className="dashboard-grid">
            {/* Left: Sidebar */}
            <StrategySidebar
              strategies={strategies}
              selectedStrategyId={selectedStrategyId}
              onSelect={handleSelectStrategy}
            />

            {/* Middle: Configure */}
            <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
                Configure
              </Typography>

              {!selectedStrategy && (
                <Typography variant="body2" color="text.secondary">
                  Select a strategy from the left panel to get started.
                </Typography>
              )}

              {selectedStrategy && (
                <>
                  <Box>
                    <Typography variant="h6" sx={{ fontWeight: 900 }}>
                      {selectedStrategy.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedStrategy.description}
                    </Typography>
                    {selectedEducation?.rebalanceFrequency && (
                      <Box sx={{ mt: 1 }}>
                        <Chip label={`Rebalance: ${selectedEducation.rebalanceFrequency}`} size="small" />
                      </Box>
                    )}
                  </Box>

                  {selectedEducation && <StrategyAboutPanel education={selectedEducation} />}

                  <Divider />

                  <TextField
                    fullWidth
                    label="Investment Amount"
                    type="number"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    placeholder="Enter amount in $"
                    InputProps={{
                      startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                    }}
                  />

                  {/* Strategy-specific UI for parameters (PAA/VAA), with a generic fallback. */}
                  <ConfigPanel strategy={selectedStrategy} paramValues={paramValues} onParamChange={handleParamChange} />

                  <Box sx={{ display: 'flex', gap: 1.5 }}>
                    <Button
                      variant="contained"
                      startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <CalculateIcon />}
                      onClick={handleCalculate}
                      disabled={loading}
                    >
                      {loading ? 'Calculating...' : 'Calculate'}
                    </Button>
                    <Button variant="outlined" onClick={handleReset} disabled={loading}>
                      Reset
                    </Button>
                  </Box>
                </>
              )}
            </Paper>

            {/* Right: Results */}
            <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
                Results
              </Typography>

              {!results && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Run a calculation to see allocation charts and a breakdown table.
                </Typography>
              )}

              {results && (
                <>
                  {/* Scrollable top area so the table stays in a consistent position/size. */}
                  <Box sx={{ flex: 1, overflow: 'auto', mt: 1, pr: 1 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        Strategy
                      </Typography>
                      <Typography variant="h6" sx={{ fontWeight: 900 }}>
                        {results.strategy}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total: ${Number(results.totalAmount).toLocaleString()}
                      </Typography>
                      {selectedEducation?.rebalanceFrequency && (
                        <Box sx={{ mt: 1 }}>
                          <Chip label={`Rebalance: ${selectedEducation.rebalanceFrequency}`} size="small" />
                        </Box>
                      )}
                    </Box>

                    {results.metadata?.missing_tickers && results.metadata.missing_tickers.length > 0 && (
                      <Alert severity="warning" sx={{ mt: 1 }}>
                        Missing tickers: {results.metadata.missing_tickers.join(', ')}
                      </Alert>
                    )}

                    <Divider sx={{ my: 2 }} />

                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
                        Allocation Chart
                      </Typography>
                      <AllocationDonutChart data={donutData} />
                    </Box>

                    <Box sx={{ minHeight: 10 }} />

                    {momentumScores && (
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
                          Momentum Chart
                        </Typography>
                        <MomentumBarChart scores={momentumScores} />
                      </Box>
                    )}

                    {results.metadata && (
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
                        {typeof results.metadata.defensive_ratio === 'number' && (
                          <Chip label={`Defensive ${(results.metadata.defensive_ratio * 100).toFixed(1)}%`} />
                        )}
                        {typeof results.metadata.offensive_ratio === 'number' && (
                          <Chip label={`Offensive ${(results.metadata.offensive_ratio * 100).toFixed(1)}%`} />
                        )}
                        {typeof results.metadata.avg_momentum === 'number' && (
                          <Chip label={`Avg ${(results.metadata.avg_momentum * 100).toFixed(2)}%`} />
                        )}
                        {results.metadata.selected_asset && <Chip label={`Selected ${results.metadata.selected_asset}`} />}
                        {results.metadata.mode && <Chip label={`${String(results.metadata.mode).toUpperCase()}`} />}
                      </Box>
                    )}
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ flexShrink: 0 }}>
                    <ResultsTable rows={results.breakdown} momentumScores={momentumScores} />
                  </Box>
                </>
              )}
            </Paper>
          </Box>
        </Box>
      </Container>
    </div>
  );
};

export default Dashboard;
