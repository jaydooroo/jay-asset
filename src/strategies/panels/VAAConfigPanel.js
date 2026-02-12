import React from 'react';
import { Box, Grid, TextField, Typography } from '@mui/material';
import { parseCommaTickers } from '../utils';

// Custom UI for VAA so the two buckets are clearly shown.
const VAAConfigPanel = ({ paramValues, onParamChange }) => {
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        VAA Parameters
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Offensive Assets"
            value={paramValues.offensive_assets ?? ''}
            onChange={(e) => onParamChange('offensive_assets', e.target.value)}
            helperText="Comma-separated tickers (book default: SPY,EFA,EEM,AGG)"
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Defensive Assets"
            value={paramValues.defensive_assets ?? ''}
            onChange={(e) => onParamChange('defensive_assets', e.target.value)}
            helperText="Comma-separated tickers (book default: LQD,IEF,SHY)"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export const buildVAAParameters = (paramValues) => {
  const parameters = {};
  const offensive = parseCommaTickers(paramValues.offensive_assets);
  const defensive = parseCommaTickers(paramValues.defensive_assets);
  if (offensive.length > 0) parameters.offensive_assets = offensive;
  if (defensive.length > 0) parameters.defensive_assets = defensive;
  return parameters;
};

export default VAAConfigPanel;

