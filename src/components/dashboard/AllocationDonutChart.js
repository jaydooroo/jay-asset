import React from 'react';
import { Box, Typography } from '@mui/material';
import { useLanguage } from '../../i18n/LanguageContext';

const DEFAULT_COLORS = [
  '#4F46E5',
  '#06B6D4',
  '#10B981',
  '#F59E0B',
  '#EF4444',
  '#A855F7',
  '#64748B',
  '#22C55E',
  '#FB7185',
  '#60A5FA',
];

const clamp01 = (value) => Math.max(0, Math.min(1, value));

// Simple SVG donut chart with a small legend.
// data: [{ label: 'SPY', value: 25.0 }, ...] where value is percentage (0..100).
const AllocationDonutChart = ({ data, size = 160, thickness = 18, colors = DEFAULT_COLORS }) => {
  const { t } = useLanguage();
  if (!data || data.length === 0) return null;

  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;

  const normalized = data
    .map((slice) => ({
      ...slice,
      value: Number(slice.value) || 0,
    }))
    .filter((slice) => slice.value > 0);

  const total = normalized.reduce((sum, slice) => sum + slice.value, 0);
  if (total <= 0) return null;

  let offset = 0;

  return (
    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
      <Box sx={{ position: 'relative', width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
            <circle
              cx={size / 2}
              cy={size / 2}
              r={radius}
              stroke="#E5E7EB"
              strokeWidth={thickness}
              fill="none"
            />
            {normalized.map((slice, idx) => {
              const fraction = clamp01(slice.value / total);
              const dash = fraction * circumference;
              const dashArray = `${dash} ${circumference - dash}`;
              const dashOffset = -offset * circumference;
              offset += fraction;

              return (
                <circle
                  key={slice.label}
                  cx={size / 2}
                  cy={size / 2}
                  r={radius}
                  stroke={colors[idx % colors.length]}
                  strokeWidth={thickness}
                  strokeLinecap="butt"
                  fill="none"
                  strokeDasharray={dashArray}
                  strokeDashoffset={dashOffset}
                />
              );
            })}
          </g>
        </svg>
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexDirection: 'column',
            pointerEvents: 'none',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            {t('chart.allocation')}
          </Typography>
          <Typography variant="subtitle2" sx={{ fontWeight: 800 }}>
            100%
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'grid', gap: 0.5 }}>
        {normalized.slice(0, 8).map((slice, idx) => (
          <Box key={slice.label} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 10,
                height: 10,
                borderRadius: '2px',
                backgroundColor: colors[idx % colors.length],
              }}
            />
            <Typography variant="body2" sx={{ minWidth: 42 }}>
              {slice.label}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {slice.value.toFixed(1)}%
            </Typography>
          </Box>
        ))}
        {normalized.length > 8 && (
          <Typography variant="caption" color="text.secondary">
            {t('chart.more', { count: normalized.length - 8 })}
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default AllocationDonutChart;
