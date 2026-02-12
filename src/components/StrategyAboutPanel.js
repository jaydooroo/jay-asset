import React from 'react';
import { Box, Chip, Paper, Typography } from '@mui/material';

const StrategyAboutPanel = ({ education }) => {
  if (!education) return null;

  return (
    <Paper elevation={1} sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, mb: 1 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
          About: {education.title}
        </Typography>
        {education.rebalanceFrequency && (
          <Chip label={`Rebalance: ${education.rebalanceFrequency}`} size="small" />
        )}
      </Box>

      {education.sections.map((section) => (
        <Box key={section.heading} sx={{ mb: 1.5 }}>
          <Typography variant="body2" sx={{ fontWeight: 700 }}>
            {section.heading}
          </Typography>
          <Box component="ul" sx={{ mt: 0.5, mb: 0, pl: 2 }}>
            {section.bullets.map((bullet) => (
              <Box component="li" key={bullet}>
                <Typography variant="body2" color="text.secondary">
                  {bullet}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>
      ))}
    </Paper>
  );
};

export default StrategyAboutPanel;
