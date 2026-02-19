import React, { useMemo, useState } from 'react';
import {
  Box,
  Chip,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import { useLanguage } from '../../i18n/LanguageContext';

const StrategySidebar = ({ strategies, selectedStrategyId, onSelect }) => {
  const { t } = useLanguage();
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState('all'); // all | static | dynamic

  const filtered = useMemo(() => {
    const entries = Object.entries(strategies || {});
    const q = query.trim().toLowerCase();

    return entries
      .filter(([, strategy]) => {
        if (filter === 'static' && strategy.type !== 'static') return false;
        if (filter === 'dynamic' && strategy.type !== 'dynamic') return false;
        if (!q) return true;
        return (
          String(strategy.name || '').toLowerCase().includes(q) ||
          String(strategy.description || '').toLowerCase().includes(q)
        );
      })
      .sort((a, b) => String(a[1].name).localeCompare(String(b[1].name)));
  }, [strategies, query, filter]);

  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', gap: 1.5 }}>
      <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
        {t('sidebar.strategies')}
      </Typography>

      <TextField
        size="small"
        placeholder={t('sidebar.searchPlaceholder')}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        <Chip label={t('sidebar.all')} clickable color={filter === 'all' ? 'primary' : 'default'} onClick={() => setFilter('all')} />
        <Chip label={t('sidebar.static')} clickable color={filter === 'static' ? 'primary' : 'default'} onClick={() => setFilter('static')} />
        <Chip label={t('sidebar.live')} clickable color={filter === 'dynamic' ? 'primary' : 'default'} onClick={() => setFilter('dynamic')} />
      </Box>

      <Divider />

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List dense disablePadding>
          {filtered.map(([id, strategy]) => (
            <ListItemButton
              key={id}
              selected={id === selectedStrategyId}
              onClick={() => onSelect(id)}
              sx={{ borderRadius: 1, mb: 0.5 }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 700 }}>
                      {strategy.name}
                    </Typography>
                    {strategy.type === 'dynamic' && <Chip label={t('sidebar.live')} size="small" />}
                  </Box>
                }
                secondary={
                  <Typography variant="caption" color="text.secondary">
                    {strategy.description}
                  </Typography>
                }
              />
            </ListItemButton>
          ))}
          {filtered.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
              {t('sidebar.noStrategies')}
            </Typography>
          )}
        </List>
      </Box>
    </Paper>
  );
};

export default StrategySidebar;
