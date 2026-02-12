import React from 'react';
import { Box, Grid, TextField, Typography } from '@mui/material';
import { parseCommaTickers, parseNumber } from '../utils';

// Custom UI for PAA so the parameter inputs feel more intentional than a generic form.
const PAAConfigPanel = ({ paramValues, onParamChange }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        PAA Parameters
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="ETF Tickers"
            value={paramValues.etfs ?? ''}
            onChange={(e) => onParamChange('etfs', e.target.value)}
            helperText="Comma-separated tickers (e.g., SPY, QQQ, IWM)"
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Top N ETFs"
            type="number"
            value={paramValues.top_n ?? ''}
            onChange={(e) => onParamChange('top_n', e.target.value)}
            helperText="Number of top-performing ETFs to consider"
            inputProps={{ min: 1, max: 12, step: 1 }}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Lookback (Months)"
            type="number"
            value={paramValues.lookback_months ?? ''}
            onChange={(e) => onParamChange('lookback_months', e.target.value)}
            helperText="Used for momentum calculation (moving average)"
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

