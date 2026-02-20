import React, { useEffect, useMemo, useState } from 'react';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Alert,
  Box,
  Button,
  Chip,
  Container,
  Divider,
  FormControl,
  Grid,
  InputAdornment,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography,
  CircularProgress,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import TuneIcon from '@mui/icons-material/Tune';

import ApiService from '../services/api';
import StrategyAboutPanel from '../components/StrategyAboutPanel';
import AllocationDonutChart from '../components/dashboard/AllocationDonutChart';
import MomentumBarChart from '../components/dashboard/MomentumBarChart';
import PerformanceSummary from '../components/dashboard/PerformanceSummary';
import ResultsTable from '../components/dashboard/ResultsTable';
import { staticStrategies } from '../data/staticStrategies';
import { strategyEducation, strategyEducationKo } from '../data/strategyEducation';
import { buildStrategyParameters, getStrategyConfigPanel } from '../strategies/registry';
import { useLanguage } from '../i18n/LanguageContext';
import './Dashboard.css';

const Dashboard = () => {
  const { language, t } = useLanguage();
  const [dynamicStrategies, setDynamicStrategies] = useState({});
  const [selectedStrategyId, setSelectedStrategyId] = useState('');
  const [amount, setAmount] = useState('');
  const [paramValues, setParamValues] = useState({});
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendAvailable, setBackendAvailable] = useState(false);

  const [performanceByStrategy, setPerformanceByStrategy] = useState({});
  const [performanceLoading, setPerformanceLoading] = useState(false);
  const [performanceError, setPerformanceError] = useState(null);

  const buildDefaultParams = (strategy) => {
    if (!strategy || !Array.isArray(strategy.parameters) || strategy.parameters.length === 0) {
      return {};
    }
    const defaults = {};
    strategy.parameters.forEach((param) => {
      defaults[param.name] = param.default ?? '';
    });
    return defaults;
  };

  useEffect(() => {
    const load = async () => {
      try {
        await ApiService.healthCheck();
        setBackendAvailable(true);
        const dynamic = await ApiService.getStrategies();
        setDynamicStrategies(dynamic);
      } catch {
        setBackendAvailable(false);
      }
    };
    load();
  }, []);

  const strategies = useMemo(() => {
    const merged = { ...staticStrategies };
    Object.keys(dynamicStrategies).forEach((key) => {
      const raw = dynamicStrategies[key];
      const localizedName = t(`strategies.${key}.name`);
      const localizedDescription = t(`strategies.${key}.description`);
      merged[key] = {
        ...raw,
        name: localizedName === `strategies.${key}.name` ? raw.name : localizedName,
        description:
          localizedDescription === `strategies.${key}.description` ? raw.description : localizedDescription,
        type: 'dynamic',
      };
    });
    return merged;
  }, [dynamicStrategies, t]);

  const strategyEntries = useMemo(
    () => Object.entries(strategies).sort((a, b) => String(a[1].name).localeCompare(String(b[1].name))),
    [strategies]
  );

  useEffect(() => {
    if (selectedStrategyId || strategyEntries.length === 0) return;

    const preferred = strategyEntries.some(([id]) => id === 'paa')
      ? 'paa'
      : strategyEntries[0][0];

    setSelectedStrategyId(preferred);
    setParamValues(buildDefaultParams(strategies[preferred]));
  }, [selectedStrategyId, strategyEntries, strategies]);

  const selectedStrategy = selectedStrategyId ? strategies[selectedStrategyId] : null;
  const selectedPerformance = selectedStrategyId ? performanceByStrategy[selectedStrategyId] : null;
  const selectedEducation = selectedStrategyId
    ? (language === 'ko' ? strategyEducationKo[selectedStrategyId] : null) || strategyEducation[selectedStrategyId]
    : null;

  useEffect(() => {
    let alive = true;

    const loadPerformance = async () => {
      if (!backendAvailable || !selectedStrategyId) return;
      const strategy = strategies[selectedStrategyId];
      if (!strategy || strategy.type !== 'dynamic') return;
      if (selectedPerformance) return;

      setPerformanceLoading(true);
      setPerformanceError(null);
      try {
        const payload = await ApiService.getPerformance(selectedStrategyId);
        if (!alive) return;
        setPerformanceByStrategy((prev) => ({ ...prev, [selectedStrategyId]: payload }));
      } catch (err) {
        if (!alive) return;
        setPerformanceError(err.message || t('dashboard.performanceUnavailable'));
      } finally {
        if (alive) setPerformanceLoading(false);
      }
    };

    loadPerformance();
    return () => {
      alive = false;
    };
  }, [backendAvailable, selectedStrategyId, selectedPerformance, strategies, t]);

  const handleSelectStrategy = (id) => {
    setSelectedStrategyId(id);
    setResults(null);
    setError(null);
    setPerformanceError(null);
    setParamValues(buildDefaultParams(strategies[id]));
  };

  const handleParamChange = (name, value) => {
    setParamValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setAmount('');
    setResults(null);
    setError(null);
    setPerformanceError(null);
    setParamValues(buildDefaultParams(selectedStrategy));
  };

  const handleCalculate = async () => {
    if (!selectedStrategyId || !amount || Number(amount) <= 0) {
      setError(t('dashboard.errorSelectAmount'));
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const totalAmount = Number.parseFloat(amount);
      const strategy = strategies[selectedStrategyId];

      if (!strategy) {
        setError(t('dashboard.errorSelectStrategy'));
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
          strategyId: selectedStrategyId,
        });
        return;
      }

      const parameters = buildStrategyParameters(selectedStrategyId, strategy.parameters, paramValues);
      const result = await ApiService.calculateAllocation(selectedStrategyId, totalAmount, parameters);

      const breakdown = Object.entries(result.allocation).map(([asset, amt]) => ({
        asset,
        amount: Number(amt),
        percentage: (Number(amt) / totalAmount) * 100,
      }));

      if (result.momentum_scores) {
        const scores = result.momentum_scores;
        breakdown.sort(
          (a, b) => (scores[b.asset] ?? Number.NEGATIVE_INFINITY) - (scores[a.asset] ?? Number.NEGATIVE_INFINITY)
        );
      } else {
        breakdown.sort((a, b) => b.percentage - a.percentage);
      }

      setResults({
        strategy: result.strategy,
        description: strategy.description,
        totalAmount,
        breakdown,
        type: 'dynamic',
        strategyId: selectedStrategyId,
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
      <Container maxWidth="xl" className="dashboard-content">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 2, md: 2.4 },
            borderRadius: 3,
            border: '1px solid var(--surface-border)',
            backgroundColor: 'rgba(255,255,255,0.9)',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: { xs: 'flex-start', md: 'center' }, gap: 1.2, flexWrap: 'wrap' }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h4" sx={{ fontWeight: 900, fontSize: { xs: '1.4rem', md: '1.9rem' }, mb: 0.6 }}>
                {t('dashboard.title')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('dashboard.subtitle')}
              </Typography>
            </Box>
            {backendAvailable && <Chip label={t('dashboard.backendConnected')} color="success" size="small" />}
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Paper
          elevation={0}
          sx={{
            p: { xs: 2, md: 2.4 },
            borderRadius: 3,
            border: '1px solid var(--surface-border)',
            backgroundColor: 'rgba(255,255,255,0.9)',
          }}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1.5 }}>
            {t('dashboard.quickActionTitle')}
          </Typography>

          <Grid container spacing={1.6}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="strategy-select-label">{t('dashboard.strategySelectLabel')}</InputLabel>
                <Select
                  labelId="strategy-select-label"
                  value={selectedStrategyId}
                  label={t('dashboard.strategySelectLabel')}
                  onChange={(e) => handleSelectStrategy(String(e.target.value))}
                  MenuProps={{
                    disableScrollLock: true,
                    PaperProps: {
                      sx: {
                        maxWidth: 'calc(100vw - 24px)',
                      },
                    },
                  }}
                >
                  {strategyEntries.map(([id, strategy]) => (
                    <MenuItem key={id} value={id}>
                      {strategy.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={t('dashboard.investmentAmount')}
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder={t('dashboard.amountPlaceholder')}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
          </Grid>

          {selectedStrategy && (
            <Box sx={{ mt: 1.6 }}>
              <Typography variant="body1" sx={{ fontWeight: 700 }}>
                {selectedStrategy.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {selectedStrategy.description}
              </Typography>
              {selectedEducation?.rebalanceFrequency && (
                <Chip
                  label={t('dashboard.rebalance', { value: selectedEducation.rebalanceFrequency })}
                  size="small"
                  sx={{ mt: 1 }}
                />
              )}
            </Box>
          )}

          <Box sx={{ mt: 1.8, display: 'flex', gap: 1.2, flexWrap: { xs: 'wrap', sm: 'nowrap' } }}>
            <Button
              variant="contained"
              startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <CalculateIcon />}
              onClick={handleCalculate}
              disabled={loading || !selectedStrategyId}
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                px: 2.2,
                textTransform: 'none',
                fontWeight: 700,
                background: 'linear-gradient(135deg, #0e7490 0%, #2563eb 100%)',
              }}
            >
              {loading ? t('dashboard.calculating') : t('dashboard.calculate')}
            </Button>
            <Button
              variant="outlined"
              onClick={handleReset}
              disabled={loading || !selectedStrategyId}
              sx={{
                flex: { xs: '1 1 100%', sm: '1 1 auto' },
                textTransform: 'none',
                fontWeight: 700,
              }}
            >
              {t('dashboard.reset')}
            </Button>
          </Box>

          {selectedStrategy && (
            <Accordion
              expanded={showAdvanced}
              onChange={(_, expanded) => setShowAdvanced(expanded)}
              disableGutters
              elevation={0}
              sx={{
                mt: 1.8,
                backgroundColor: 'transparent',
                border: '1px solid var(--surface-border)',
                borderRadius: '14px !important',
                '&::before': { display: 'none' },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{ minHeight: 48 }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TuneIcon sx={{ fontSize: 18 }} />
                  <Typography sx={{ fontWeight: 700 }}>{t('dashboard.advancedSettings')}</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <ConfigPanel strategy={selectedStrategy} paramValues={paramValues} onParamChange={handleParamChange} />
                {selectedEducation && (
                  <>
                    <Divider sx={{ my: 2 }} />
                    <StrategyAboutPanel education={selectedEducation} />
                  </>
                )}
              </AccordionDetails>
            </Accordion>
          )}
        </Paper>

        <Paper
          elevation={0}
          sx={{
            p: { xs: 2, md: 2.4 },
            borderRadius: 3,
            border: '1px solid var(--surface-border)',
            backgroundColor: 'rgba(255,255,255,0.9)',
            minWidth: 0,
          }}
        >
          <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
            {t('dashboard.results')}
          </Typography>

          {selectedStrategy && selectedStrategy.type === 'dynamic' && (
            <PerformanceSummary payload={selectedPerformance} loading={performanceLoading} error={performanceError} />
          )}

          {!results && (
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              {t('dashboard.runPrompt')}
            </Typography>
          )}

          {results && (
            <>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  {t('dashboard.strategy')}
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 900 }}>
                  {results.strategy}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('dashboard.total', { currency: '$', total: Number(results.totalAmount).toLocaleString() })}
                </Typography>
              </Box>

              {results.metadata?.missing_tickers && results.metadata.missing_tickers.length > 0 && (
                <Alert severity="warning" sx={{ mt: 1.2 }}>
                  {t('dashboard.missingTickers', { tickers: results.metadata.missing_tickers.join(', ') })}
                </Alert>
              )}

              <Divider sx={{ my: 2 }} />

              <Box className="results-grid">
                <Box className="results-scroll">
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
                      {t('dashboard.allocationChart')}
                    </Typography>
                    <AllocationDonutChart data={donutData} strategyId={results.strategyId} />
                  </Box>

                  <Box sx={{ minHeight: 12 }} />

                  {momentumScores && (
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
                        {t('dashboard.momentumChart')}
                      </Typography>
                      <MomentumBarChart scores={momentumScores} strategyId={results.strategyId} />
                    </Box>
                  )}

                  {results.metadata && (
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
                      {typeof results.metadata.defensive_ratio === 'number' && (
                        <Chip label={t('dashboard.defensive', { value: (results.metadata.defensive_ratio * 100).toFixed(1) })} />
                      )}
                      {typeof results.metadata.offensive_ratio === 'number' && (
                        <Chip label={t('dashboard.offensive', { value: (results.metadata.offensive_ratio * 100).toFixed(1) })} />
                      )}
                      {typeof results.metadata.avg_momentum === 'number' && (
                        <Chip label={t('dashboard.avg', { value: (results.metadata.avg_momentum * 100).toFixed(2) })} />
                      )}
                      {results.metadata.selected_asset && <Chip label={t('dashboard.selected', { value: results.metadata.selected_asset })} />}
                      {results.metadata.mode && <Chip label={`${String(results.metadata.mode).toUpperCase()}`} />}
                    </Box>
                  )}
                </Box>

                <Box sx={{ minWidth: 0 }}>
                  <ResultsTable
                    rows={results.breakdown}
                    momentumScores={momentumScores}
                    strategyId={results.strategyId}
                  />
                </Box>
              </Box>
            </>
          )}
        </Paper>
      </Container>
    </div>
  );
};

export default Dashboard;
