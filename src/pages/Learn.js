import React, { useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  Chip,
  Container,
  Divider,
  Grid,
  LinearProgress,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';
import CheckCircleRoundedIcon from '@mui/icons-material/CheckCircleRounded';
import RadioButtonUncheckedRoundedIcon from '@mui/icons-material/RadioButtonUncheckedRounded';
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded';
import OpenInNewRoundedIcon from '@mui/icons-material/OpenInNewRounded';
import { Link } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';

const PROGRESS_STORAGE_KEY = 'jay-asset-learn-progress-v1';
const STEP_IDS = [
  'chooseStrategy',
  'enterAmount',
  'runCalculation',
  'readAllocation',
  'readPerformance',
  'resetAndAdvanced',
];

const asArray = (value) => (Array.isArray(value) ? value : []);
const asText = (value, fallback = '') => {
  if (typeof value !== 'string') return fallback;
  return value.startsWith('learn.') ? fallback : value;
};

const Learn = () => {
  const { t } = useLanguage();
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [completedMap, setCompletedMap] = useState({});

  const steps = useMemo(
    () =>
      STEP_IDS.map((id) => ({
        id,
        title: asText(t(`learn.steps.${id}.title`), id),
        whatThisDoes: asArray(t(`learn.steps.${id}.whatThisDoes`)),
        whatToClick: asArray(t(`learn.steps.${id}.whatToClick`)),
        expectedResult: asArray(t(`learn.steps.${id}.expectedResult`)),
        commonMistake: asText(t(`learn.steps.${id}.commonMistake`)),
      })),
    [t]
  );

  const currentStep = steps[currentStepIndex] || null;
  const completedCount = useMemo(
    () => steps.reduce((count, _, index) => count + (completedMap[index] ? 1 : 0), 0),
    [completedMap, steps]
  );
  const progressPct = steps.length > 0 ? (completedCount / steps.length) * 100 : 0;

  useEffect(() => {
    try {
      const raw = localStorage.getItem(PROGRESS_STORAGE_KEY);
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed && typeof parsed === 'object') {
        if (parsed.completed && typeof parsed.completed === 'object') {
          setCompletedMap(parsed.completed);
        }
        if (Number.isInteger(parsed.currentStepIndex)) {
          setCurrentStepIndex(Math.max(0, Math.min(parsed.currentStepIndex, STEP_IDS.length - 1)));
        }
      }
    } catch {
      // Ignore invalid saved progress.
    }
  }, []);

  useEffect(() => {
    const payload = JSON.stringify({
      currentStepIndex,
      completed: completedMap,
    });
    localStorage.setItem(PROGRESS_STORAGE_KEY, payload);
  }, [currentStepIndex, completedMap]);

  const setStepComplete = (index) => {
    setCompletedMap((prev) => ({ ...prev, [index]: true }));
  };

  const handleStartTutorial = () => {
    setCurrentStepIndex(0);
  };

  const handleBack = () => {
    setCurrentStepIndex((prev) => Math.max(0, prev - 1));
  };

  const handleNext = () => {
    setStepComplete(currentStepIndex);
    setCurrentStepIndex((prev) => Math.min(steps.length - 1, prev + 1));
  };

  const refs = [
    {
      title: t('learn.references.paaVaaTitle'),
      body: t('learn.references.paaVaaBody'),
    },
    {
      title: t('learn.references.metricsTitle'),
      body: t('learn.references.metricsBody'),
    },
    {
      title: t('learn.references.troubleshootingTitle'),
      body: t('learn.references.troubleshootingBody'),
    },
    {
      title: t('learn.references.faqTitle'),
      body: t('learn.references.faqBody'),
    },
  ];

  const renderBulletSection = (title, lines) => {
    if (!Array.isArray(lines) || lines.length === 0) return null;
    return (
      <Box>
        <Typography sx={{ fontWeight: 800, mb: 0.6 }}>{title}</Typography>
        <Box component="ul" sx={{ mt: 0, mb: 0, pl: 2.5 }}>
          {lines.map((line) => (
            <Box component="li" key={line} sx={{ mb: 0.45 }}>
              <Typography variant="body2" color="text.secondary">
                {line}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Box sx={{ minHeight: 'calc(100vh - 92px)', py: { xs: 2, md: 3 } }}>
      <Container maxWidth="xl">
        <Paper
          elevation={0}
          sx={{
            p: { xs: 2, md: 2.8 },
            borderRadius: 3,
            border: '1px solid var(--surface-border)',
            backgroundColor: 'rgba(255,255,255,0.9)',
            mb: 2,
          }}
        >
          <Typography variant="h4" sx={{ fontWeight: 900, fontSize: { xs: '1.5rem', md: '2rem' }, mb: 0.8 }}>
            {t('learn.title')}
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 1.8 }}>
            {t('learn.subtitle')}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button
              variant="contained"
              startIcon={<PlayArrowRoundedIcon />}
              onClick={handleStartTutorial}
              sx={{
                textTransform: 'none',
                fontWeight: 700,
                background: 'linear-gradient(135deg, #0e7490 0%, #2563eb 100%)',
              }}
            >
              {t('learn.actions.startTutorial')}
            </Button>
            <Button
              variant="outlined"
              component={Link}
              to="/"
              endIcon={<OpenInNewRoundedIcon />}
              sx={{ textTransform: 'none', fontWeight: 700 }}
            >
              {t('learn.actions.jumpDashboard')}
            </Button>
          </Box>
        </Paper>

        <Grid container spacing={2}>
          <Grid item xs={12} lg={4}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                borderRadius: 3,
                border: '1px solid var(--surface-border)',
                backgroundColor: 'rgba(255,255,255,0.88)',
                position: { lg: 'sticky' },
                top: { lg: 96 },
              }}
            >
              <Typography variant="subtitle1" sx={{ fontWeight: 800 }}>
                {t('learn.progressTitle')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {t('learn.progressCount', { done: completedCount, total: steps.length })}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={progressPct}
                sx={{ mt: 1, mb: 1.2, height: 8, borderRadius: 999 }}
              />
              <List dense disablePadding>
                {steps.map((step, index) => (
                  <ListItemButton
                    key={step.id}
                    selected={index === currentStepIndex}
                    onClick={() => setCurrentStepIndex(index)}
                    sx={{ borderRadius: 2, mb: 0.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 30 }}>
                      {completedMap[index] ? (
                        <CheckCircleRoundedIcon color="success" fontSize="small" />
                      ) : (
                        <RadioButtonUncheckedRoundedIcon sx={{ color: 'text.disabled', fontSize: 18 }} />
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography variant="body2" sx={{ fontWeight: index === currentStepIndex ? 700 : 500 }}>
                          {step.title}
                        </Typography>
                      }
                    />
                  </ListItemButton>
                ))}
              </List>
            </Paper>
          </Grid>

          <Grid item xs={12} lg={8}>
            <Paper
              elevation={0}
              sx={{
                p: { xs: 2, md: 2.4 },
                borderRadius: 3,
                border: '1px solid var(--surface-border)',
                backgroundColor: 'rgba(255,255,255,0.9)',
                mb: 2,
              }}
            >
              {currentStep && (
                <>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
                    <Chip
                      color="primary"
                      size="small"
                      label={t('learn.stepLabel', { current: currentStepIndex + 1, total: steps.length })}
                    />
                    {completedMap[currentStepIndex] && (
                      <Chip
                        size="small"
                        color="success"
                        icon={<CheckCircleRoundedIcon />}
                        label={t('learn.completedTag')}
                      />
                    )}
                  </Box>

                  <Typography variant="h5" sx={{ fontWeight: 900, mt: 1.2, mb: 2 }}>
                    {currentStep.title}
                  </Typography>

                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      {renderBulletSection(t('learn.sections.whatThisDoes'), currentStep.whatThisDoes)}
                    </Grid>
                    <Grid item xs={12} md={6}>
                      {renderBulletSection(t('learn.sections.whatToClick'), currentStep.whatToClick)}
                    </Grid>
                    <Grid item xs={12}>
                      {renderBulletSection(t('learn.sections.expectedResult'), currentStep.expectedResult)}
                    </Grid>
                  </Grid>

                  {currentStep.commonMistake && (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      <Typography sx={{ fontWeight: 700, mb: 0.3 }}>{t('learn.sections.commonMistake')}</Typography>
                      <Typography variant="body2">{currentStep.commonMistake}</Typography>
                    </Alert>
                  )}

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="outlined"
                      startIcon={<OpenInNewRoundedIcon />}
                      component={Link}
                      to="/"
                      sx={{ textTransform: 'none', fontWeight: 700 }}
                    >
                      {t('learn.actions.tryOnDashboard')}
                    </Button>
                    <Button
                      variant="text"
                      onClick={() => setStepComplete(currentStepIndex)}
                      sx={{ textTransform: 'none', fontWeight: 700 }}
                    >
                      {t('learn.actions.markComplete')}
                    </Button>
                    <Box sx={{ flex: 1 }} />
                    <Button
                      variant="outlined"
                      startIcon={<ArrowBackRoundedIcon />}
                      onClick={handleBack}
                      disabled={currentStepIndex === 0}
                      sx={{ textTransform: 'none', fontWeight: 700 }}
                    >
                      {t('learn.actions.back')}
                    </Button>
                    <Button
                      variant="contained"
                      endIcon={<ArrowForwardRoundedIcon />}
                      onClick={handleNext}
                      sx={{
                        textTransform: 'none',
                        fontWeight: 700,
                        background: 'linear-gradient(135deg, #0e7490 0%, #2563eb 100%)',
                      }}
                    >
                      {currentStepIndex === steps.length - 1
                        ? t('learn.actions.finish')
                        : t('learn.actions.next')}
                    </Button>
                  </Box>
                </>
              )}
            </Paper>

            <Paper
              elevation={0}
              sx={{
                p: { xs: 2, md: 2.4 },
                borderRadius: 3,
                border: '1px solid var(--surface-border)',
                backgroundColor: 'rgba(255,255,255,0.9)',
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 800, mb: 1.5 }}>
                {t('learn.references.title')}
              </Typography>
              <Grid container spacing={1.5}>
                {refs.map((section) => (
                  <Grid item xs={12} md={6} key={section.title}>
                    <Paper
                      elevation={0}
                      sx={{
                        p: 1.6,
                        borderRadius: 2,
                        border: '1px solid var(--surface-border)',
                        backgroundColor: 'var(--panel-bg)',
                        height: '100%',
                      }}
                    >
                      <Typography sx={{ fontWeight: 800, mb: 0.6 }}>{section.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {section.body}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Learn;
