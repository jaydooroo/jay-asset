import React from 'react';
import { Container, Paper, Typography } from '@mui/material';

// Simple informational page for the navbar route (/contact).
// You can replace the content with your preferred contact details.
const Contact = () => {
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 800, mb: 2 }}>
          Contact
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Add your preferred contact method here (email, GitHub, LinkedIn, etc.).
        </Typography>
      </Paper>
    </Container>
  );
};

export default Contact;

