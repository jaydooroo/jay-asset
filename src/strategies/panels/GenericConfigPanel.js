import React from 'react';
import { Box, Grid, TextField, Typography } from '@mui/material';
import { parseCommaTickers, parseNumber } from '../utils';
import { useLanguage } from '../../i18n/LanguageContext';

// Fallback config panel for any backend strategy:
// renders parameters based on the backend-provided schema.
const GenericConfigPanel = ({ strategy, paramValues, onParamChange }) => {
  const { t } = useLanguage();
  if (!strategy?.parameters || strategy.parameters.length === 0) return null;

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        {t('config.strategyParameters')}
      </Typography>
      <Grid container spacing={2}>
        {strategy.parameters.map((param) => (
          <Grid item xs={12} md={6} key={param.name}>
            <TextField
              fullWidth
              label={param.label}
              type={param.type === 'number' ? 'number' : 'text'}
              value={paramValues[param.name] ?? ''}
              onChange={(e) => {
                const raw = e.target.value;
                if (param.type === 'number') {
                  onParamChange(param.name, raw);
                  return;
                }
                onParamChange(param.name, raw);
              }}
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
    </Box>
  );
};

export const buildGenericParameters = (paramDefs, paramValues) => {
  const parameters = {};
  (paramDefs || []).forEach((param) => {
    const rawValue = paramValues[param.name];

    if (param.type === 'number') {
      const numericValue = parseNumber(rawValue);
      if (numericValue !== null) parameters[param.name] = numericValue;
      return;
    }

    if (param.name === 'etfs' || param.name.endsWith('_assets')) {
      const list = parseCommaTickers(rawValue);
      if (list.length > 0) parameters[param.name] = list;
      return;
    }

    if (rawValue !== undefined && rawValue !== null && rawValue !== '') {
      parameters[param.name] = rawValue;
    }
  });
  return parameters;
};

export default GenericConfigPanel;
