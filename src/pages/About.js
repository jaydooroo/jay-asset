import React from 'react';
import { Container, Paper, Typography } from '@mui/material';

// Simple informational page for the navbar route (/about).
// Keeps routing consistent so users don't hit a blank page/404.
const About = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 800, mb: 2 }}>
          About
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Jay Asset Management is a small web app that calculates portfolio allocations based on
          different strategies (static allocations and live-data strategies like momentum-based
          allocation).
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Disclaimer: This project is for educational purposes and is not financial advice.
        </Typography>
      </Paper>
    </Container>
  );
};

export default About;

