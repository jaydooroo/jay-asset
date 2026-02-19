import React from 'react';
import { Box, Grid, TextField, Typography } from '@mui/material';
import { parseCommaTickers, parseNumber } from '../utils';
import { useLanguage } from '../../i18n/LanguageContext';

// Custom UI for PAA so the parameter inputs feel more intentional than a generic form.
const PAAConfigPanel = ({ paramValues, onParamChange }) => {
  const { t } = useLanguage();

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        {t('config.paaParameters')}
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label={t('config.etfTickers')}
            value={paramValues.etfs ?? ''}
            onChange={(e) => onParamChange('etfs', e.target.value)}
            helperText={t('config.etfTickersHelp')}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('config.topN')}
            type="number"
            value={paramValues.top_n ?? ''}
            onChange={(e) => onParamChange('top_n', e.target.value)}
            helperText={t('config.topNHelp')}
            inputProps={{ min: 1, max: 12, step: 1 }}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label={t('config.lookbackMonths')}
            type="number"
            value={paramValues.lookback_months ?? ''}
            onChange={(e) => onParamChange('lookback_months', e.target.value)}
            helperText={t('config.lookbackMonthsHelp')}
            inputProps={{ min: 6, max: 24, step: 1 }}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export const buildPAAParameters = (paramValues) => {
  const parameters = {};

  const tickers = parseCommaTickers(paramValues.etfs);
  if (tickers.length > 0) parameters.etfs = tickers;

  const topN = parseNumber(paramValues.top_n);
  if (topN !== null) parameters.top_n = topN;

  const lookback = parseNumber(paramValues.lookback_months);
  if (lookback !== null) parameters.lookback_months = lookback;

  return parameters;
};

export default PAAConfigPanel;
