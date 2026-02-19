import React from 'react';
import { Alert, Box, Button, Chip, CircularProgress, Paper, Typography } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useLanguage } from '../../i18n/LanguageContext';

const asPercent = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';
  return `${(value * 100).toFixed(2)}%`;
};

const PerformanceSummary = ({ payload, loading, error, onRefresh }) => {
  const { t } = useLanguage();
  const metrics = payload?.metrics || {};
  const hasMetrics = Object.keys(metrics).length > 0;

  return (
    <Paper elevation={1} sx={{ p: 2, mt: 1 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>
            {t('dashboard.performanceTitle')}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {t('dashboard.performanceSubtitle')}
          </Typography>
        </Box>
        <Button
          size="small"
          variant="outlined"
          startIcon={loading ? <CircularProgress size={14} /> : <RefreshIcon fontSize="small" />}
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? t('dashboard.refreshingPerformance') : t('dashboard.refreshPerformance')}
        </Button>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mt: 1 }}>
          {error}
        </Alert>
      )}

      {!error && !hasMetrics && !loading && (
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {t('dashboard.performanceUnavailable')}
        </Typography>
      )}

      {hasMetrics && (
        <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={t('dashboard.perfReturn', { value: asPercent(metrics.cumulative_return_period) })} />
          <Chip label={t('dashboard.perfCagr', { value: asPercent(metrics.cagr_annualized) })} />
          <Chip label={t('dashboard.perfMaxDrawdown', { value: asPercent(metrics.max_drawdown_period) })} />
          <Chip label={t('dashboard.perfVolatility', { value: asPercent(metrics.volatility_annualized) })} />
          <Chip label={t('dashboard.perfWinRate', { value: asPercent(metrics.win_rate_monthly) })} />
          {typeof metrics.months_tested === 'number' && (
            <Chip label={t('dashboard.perfMonthsTested', { value: metrics.months_tested })} />
          )}
          {metrics.window_start && metrics.as_of && (
            <Chip label={t('dashboard.perfWindow', { start: metrics.window_start, end: metrics.as_of })} />
          )}
        </Box>
      )}

      {Array.isArray(metrics.missing_tickers) && metrics.missing_tickers.length > 0 && (
        <Alert severity="info" sx={{ mt: 1 }}>
          {t('dashboard.perfMissingTickers', { tickers: metrics.missing_tickers.join(', ') })}
        </Alert>
      )}
    </Paper>
  );
};

export default PerformanceSummary;
