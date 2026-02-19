import React from 'react';
import { Container, Paper, Typography } from '@mui/material';
import { useLanguage } from '../i18n/LanguageContext';

// Simple informational page for the navbar route (/about).
// Keeps routing consistent so users don't hit a blank page/404.
const About = () => {
  const { t } = useLanguage();

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 800, mb: 2 }}>
          {t('about.title')}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          {t('about.body')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('about.disclaimer')}
        </Typography>
      </Paper>
    </Container>
  );
};

export default About;
