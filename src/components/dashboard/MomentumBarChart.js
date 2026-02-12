import React from 'react';
import { Box, Typography } from '@mui/material';

// Simple horizontal bar chart for momentum scores.
// scores: object mapping ticker -> score (e.g. 0.12 or -0.05)
const MomentumBarChart = ({ scores, maxBars = 8 }) => {
  if (!scores) return null;

  const entries = Object.entries(scores)
    .map(([ticker, score]) => [ticker, Number(score)])
    .filter(([, score]) => !Number.isNaN(score))
    .sort((a, b) => b[1] - a[1])
    .slice(0, maxBars);

  if (entries.length === 0) return null;

  const maxAbs = Math.max(...entries.map(([, score]) => Math.abs(score)), 0.0001);

  return (
    <Box sx={{ display: 'grid', gap: 1 }}>
      {entries.map(([ticker, score]) => {
        const widthPct = (Math.abs(score) / maxAbs) * 100;
        const isPositive = score >= 0;

        return (
          <Box key={ticker} sx={{ display: 'grid', gridTemplateColumns: '54px 1fr 64px', gap: 1, alignItems: 'center' }}>
            <Typography variant="body2" sx={{ fontWeight: 700 }}>
              {ticker}
            </Typography>
            <Box sx={{ position: 'relative', height: 10, backgroundColor: '#E5E7EB', borderRadius: 999 }}>
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  width: `${widthPct}%`,
                  backgroundColor: isPositive ? '#10B981' : '#EF4444',
                  borderRadius: 999,
                }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'right' }}>
              {(score * 100).toFixed(2)}%
            </Typography>
          </Box>
        );
      })}
      <Typography variant="caption" color="text.secondary">
        Top {entries.length} momentum scores
      </Typography>
    </Box>
  );
};

export default MomentumBarChart;

