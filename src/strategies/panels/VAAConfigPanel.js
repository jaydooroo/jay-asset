import React from 'react';
import { Box, Grid, TextField, Typography } from '@mui/material';
import { parseCommaTickers } from '../utils';
import { useLanguage } from '../../i18n/LanguageContext';

// Custom UI for VAA so the two buckets are clearly shown.
const VAAConfigPanel = ({ paramValues, onParamChange }) => {
  const { t } = useLanguage();

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        {t('config.vaaParameters')}
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label={t('config.offensiveAssets')}
            value={paramValues.offensive_assets ?? ''}
            onChange={(e) => onParamChange('offensive_assets', e.target.value)}
            helperText={t('config.offensiveAssetsHelp')}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label={t('config.defensiveAssets')}
            value={paramValues.defensive_assets ?? ''}
            onChange={(e) => onParamChange('defensive_assets', e.target.value)}
            helperText={t('config.defensiveAssetsHelp')}
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
