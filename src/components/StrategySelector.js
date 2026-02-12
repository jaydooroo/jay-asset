import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  Grid,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ApiService from '../services/api';
import StrategyAboutPanel from './StrategyAboutPanel';
import { staticStrategies } from '../data/staticStrategies';
import { strategyEducation } from '../data/strategyEducation';

// Static strategies (original ones)
// moved to src/data/staticStrategies.js

const StrategySelector = () => {
  const [strategies, setStrategies] = useState(staticStrategies);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [amount, setAmount] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendAvailable, setBackendAvailable] = useState(false);
  const [paramValues, setParamValues] = useState({});

  useEffect(() => {
    // Check if backend is available and load dynamic strategies
    loadDynamicStrategies();
  }, []);

  const loadDynamicStrategies = async () => {
    try {
      await ApiService.healthCheck();
      setBackendAvailable(true);

      const dynamicStrategies = await ApiService.getStrategies();

      // Merge static and dynamic strategies
      const allStrategies = { ...staticStrategies };
      Object.keys(dynamicStrategies).forEach(key => {
        allStrategies[key] = {
          ...dynamicStrategies[key],
          type: 'dynamic'
        };
      });

      setStrategies(allStrategies);
    } catch (err) {
      console.log('Backend not available, using static strategies only');
      setBackendAvailable(false);
    }
  };

  const handleCalculate = async () => {
    if (!selectedStrategy || !amount || amount <= 0) {
      setError('Please select a strategy and enter a valid amount');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const strategy = strategies[selectedStrategy];
      const totalAmount = parseFloat(amount);

      if (strategy.type === 'static') {
        // Calculate static allocation
        const calculations = Object.entries(strategy.allocation).map(([asset, percentage]) => ({
          asset,
          percentage,
          amount: (totalAmount * percentage / 100).toFixed(2),
        }));

        setResults({
          strategy: strategy.name,
          description: strategy.description,
          totalAmount: totalAmount.toFixed(2),
          breakdown: calculations,
          type: 'static'
        });
      } else {
        const parameters = {};
        if (strategy.parameters && strategy.parameters.length > 0) {
          // Build a "parameters" payload to send to the backend.
          // - `strategy.parameters` describes which inputs the strategy supports (from the backend).
          // - `paramValues` holds what the user typed into the UI form (mostly strings).
          // This loop converts/cleans user input into the correct data types:
          //   - numbers -> Number
          //   - etfs text -> ["TICKER1", "TICKER2", ...]
          //   - other text -> string (only if non-empty)
          strategy.parameters.forEach((param) => {
            // Raw user input for this parameter (often a string).
            const rawValue = paramValues[param.name];
            if (param.type === 'number') {
              // Convert number inputs from string -> Number, and only include valid values.
              const numericValue = parseFloat(rawValue);
              if (!Number.isNaN(numericValue)) {
                parameters[param.name] = numericValue;
              }
              return;
            }
            if (param.name === 'etfs') {
              // The ETF list is entered as a comma-separated string (e.g. "SPY, qqq, IWM").
              // Convert it into an array of uppercase tickers and remove empty entries.
              const etfList = (rawValue || '')
                .split(',')
                .map((value) => value.trim().toUpperCase())
                .filter(Boolean);
              if (etfList.length > 0) {
                parameters[param.name] = etfList;
              }
              return;
            }
            if (param.name.endsWith('_assets')) {
              // Strategy asset lists are entered as comma-separated tickers in the UI.
              // Example: "SPY,EFA,EEM,AGG" -> ["SPY","EFA","EEM","AGG"]
              const tickers = (rawValue || '')
                .split(',')
                .map((value) => value.trim().toUpperCase())
                .filter(Boolean);
              if (tickers.length > 0) {
                parameters[param.name] = tickers;
              }
              return;
            }
            // Default behavior for text-like params: only include if user provided a non-empty value.
            if (rawValue !== undefined && rawValue !== null && rawValue !== '') {
              parameters[param.name] = rawValue;
            }
          });
        }
        // Call backend for dynamic calculation
        const result = await ApiService.calculateAllocation(
          selectedStrategy,
          totalAmount,
          parameters
        );

        // Transform backend result to match UI format
        const breakdown = Object.entries(result.allocation).map(([asset, amount]) => ({
          asset,
          amount: amount.toFixed(2),
          percentage: ((amount / totalAmount) * 100).toFixed(2)
        }));

        if (result.momentum_scores) {
          const scores = result.momentum_scores;
          breakdown.sort((a, b) => {
            const scoreA = scores[a.asset] ?? Number.NEGATIVE_INFINITY;
            const scoreB = scores[b.asset] ?? Number.NEGATIVE_INFINITY;
            return scoreB - scoreA;
          });
        }

        setResults({
          strategy: result.strategy,
          description: strategy.description,
          totalAmount: totalAmount.toFixed(2),
          breakdown: breakdown,
          type: 'dynamic',
          metadata: {
            date: result.date,
            defensive_ratio: result.defensive_ratio,
            offensive_ratio: result.offensive_ratio,
            momentum_scores: result.momentum_scores,
            avg_momentum: result.avg_momentum,
            best_etf: result.best_etf,
            worst_etf: result.worst_etf,
          }
        });
      }
    } catch (err) {
      setError(err.message || 'Failed to calculate allocation');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedStrategy('');
    setAmount('');
    setResults(null);
    setError(null);
    setParamValues({});
  };

  const handleStrategyChange = (event) => {
    const nextStrategy = event.target.value;
    setSelectedStrategy(nextStrategy);
    setResults(null);
    setError(null);

    const selected = strategies[nextStrategy];
    if (selected && selected.parameters && selected.parameters.length > 0) {
      const defaults = {};
      selected.parameters.forEach((param) => {
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

  const selectedEducation = selectedStrategy ? strategyEducation[selectedStrategy] : null;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Card elevation={3} className="calculator-card">
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 2 }}>
            <TrendingUpIcon sx={{ fontSize: 40 }} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
              Asset Allocation Calculator
            </Typography>
          </Box>

          {backendAvailable && (
            <Chip
              label="Backend Connected"
              color="success"
              size="small"
              sx={{ mb: 2 }}
            />
          )}

          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
            Select an investment strategy and enter your amount to see how to allocate your assets
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="strategy-label">Investment Strategy</InputLabel>
                <Select
                  labelId="strategy-label"
                  value={selectedStrategy}
                  label="Investment Strategy"
                  onChange={handleStrategyChange}
                >
                  {Object.entries(strategies).map(([key, strategy]) => (
                    <MenuItem key={key} value={key}>
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body1" component="span">
                            {strategy.name}
                          </Typography>
                          {strategy.type === 'dynamic' && (
                            <Chip label="Live Data" size="small" />
                          )}
                        </Box>
                        <Typography variant="caption" color="text.secondary">
                          {strategy.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
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
            </Grid>

            {selectedStrategy && selectedEducation && (
              <Grid item xs={12}>
                <StrategyAboutPanel education={selectedEducation} />
              </Grid>
            )}

            {selectedStrategy &&
              strategies[selectedStrategy] &&
              strategies[selectedStrategy].parameters &&
              strategies[selectedStrategy].parameters.length > 0 && (
                <Grid item xs={12}>
                  <Paper elevation={1} sx={{ p: 2 }}>
                    <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                      Strategy Parameters
                    </Typography>
                    <Grid container spacing={2}>
                      {strategies[selectedStrategy].parameters.map((param) => (
                        <Grid item xs={12} md={6} key={param.name}>
                          <TextField
                            fullWidth
                            label={param.label}
                            type={param.type === 'number' ? 'number' : 'text'}
                            value={paramValues[param.name] ?? ''}
                            onChange={(e) => handleParamChange(param.name, e.target.value)}
                            helperText={param.description}
                            inputProps={{
                              min: param.min,
                              max: param.max,
                              step: param.type === 'number' ? 1 : undefined,
                            }}
                          />
                        </Grid>
                      ))}
                    </Grid>
                  </Paper>
                </Grid>
              )}

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <CalculateIcon />}
                  onClick={handleCalculate}
                  disabled={loading}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                  }}
                >
                  {loading ? 'Calculating...' : 'Calculate'}
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleReset}
                  disabled={loading}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                  }}
                >
                  Reset
                </Button>
              </Box>
            </Grid>
          </Grid>

          {results && (
            <Box sx={{ mt: 4 }}>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3, fontWeight: 'bold' }}>
                Your Asset Allocation
              </Typography>

              <Paper elevation={2} sx={{ p: 3, mb: 3, backgroundColor: '#f5f5f5' }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">Strategy</Typography>
                    <Typography variant="h6">{results.strategy}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={8}>
                    <Typography variant="body2" color="text.secondary">Description</Typography>
                    <Typography variant="body1">{results.description}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Total Investment</Typography>
                    <Typography variant="h5" color="primary">
                      ${parseFloat(results.totalAmount).toLocaleString()}
                    </Typography>
                  </Grid>

                  {results.metadata && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">Strategy Info</Typography>
                      <Box sx={{ mt: 1 }}>
                        <Chip label={`Defensive: ${(results.metadata.defensive_ratio * 100).toFixed(1)}%`} sx={{ mr: 1 }} />
                        <Chip label={`Offensive: ${(results.metadata.offensive_ratio * 100).toFixed(1)}%`} />
                        {typeof results.metadata.avg_momentum === 'number' && (
                          <Chip
                            label={`Avg Momentum: ${(results.metadata.avg_momentum * 100).toFixed(2)}%`}
                            sx={{ ml: 1 }}
                          />
                        )}
                        {results.metadata.best_etf && (
                          <Chip label={`Best: ${results.metadata.best_etf}`} sx={{ ml: 1 }} />
                        )}
                        {results.metadata.worst_etf && (
                          <Chip label={`Weakest: ${results.metadata.worst_etf}`} sx={{ ml: 1 }} />
                        )}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </Paper>

              <Grid container spacing={2}>
                {results.breakdown.map((item, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined" className="allocation-card">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {item.asset}
                        </Typography>
                        <Typography variant="h4" color="primary" sx={{ my: 1 }}>
                          ${parseFloat(item.amount).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {item.percentage}% of total
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default StrategySelector;
