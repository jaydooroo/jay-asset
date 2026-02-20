import React, { useMemo, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Container,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
  Toolbar,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import { NavLink } from 'react-router-dom';
import { useLanguage } from '../i18n/LanguageContext';
import navLogo from '../assets/jay_asset_symbol_logo.png';

const navButtonSx = {
  color: 'var(--text-strong)',
  borderRadius: 999,
  px: 1.5,
  py: 0.8,
  fontWeight: 600,
  textTransform: 'none',
  '&:hover': {
    backgroundColor: 'var(--surface-hover)',
  },
  '&.active': {
    color: 'var(--brand-accent)',
    backgroundColor: 'var(--surface-hover)',
  },
};

const Navbar = () => {
  const { language, setLanguage, t } = useLanguage();
  const [drawerOpen, setDrawerOpen] = useState(false);

  const navItems = useMemo(
    () => [
      { key: 'dashboard', label: t('navbar.dashboard'), to: '/' },
      { key: 'learn', label: t('navbar.learn'), to: '/learn' },
      { key: 'about', label: t('navbar.about'), to: '/about' },
      { key: 'contact', label: t('navbar.contact'), to: '/contact' },
    ],
    [t]
  );

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        background: 'transparent',
        color: 'var(--text-strong)',
      }}
    >
      <Container maxWidth="xl" sx={{ py: 1.25 }}>
        <Paper
          elevation={0}
          sx={{
            px: { xs: 1.2, sm: 1.8 },
            py: 0.8,
            borderRadius: 999,
            border: '1px solid var(--surface-border)',
            background: 'var(--surface-glass)',
            backdropFilter: 'blur(12px)',
            boxShadow: '0 10px 24px rgba(15, 23, 42, 0.12)',
          }}
        >
          <Toolbar disableGutters sx={{ minHeight: 'unset !important', gap: 1.25 }}>
            <Box
              component={NavLink}
              to="/"
              sx={{
                textDecoration: 'none',
                display: 'inline-flex',
                alignItems: 'center',
                gap: 1,
                color: 'inherit',
                mr: { xs: 0.5, md: 1.5 },
              }}
            >
              <Box
                sx={{
                  lineHeight: 0,
                  width: { xs: 30, sm: 34, md: 36 },
                  height: 'auto',
                  display: 'block',
                }}
                component="img"
                src={navLogo}
                alt="JAY ASSET"
                loading="eager"
              />
              <Typography
                sx={{
                  fontWeight: 800,
                  letterSpacing: '0.08em',
                  fontSize: { xs: '0.84rem', sm: '0.9rem' },
                  color: 'var(--text-strong)',
                  whiteSpace: 'nowrap',
                }}
              >
                JAY ASSET
              </Typography>
            </Box>

            <Box sx={{ display: { xs: 'none', md: 'flex' }, alignItems: 'center', gap: 0.5, flexGrow: 1 }}>
              {navItems.map((item) => (
                <Button key={item.key} component={NavLink} to={item.to} end={item.to === '/'} sx={navButtonSx}>
                  {item.label}
                </Button>
              ))}
            </Box>

            <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
              <ToggleButtonGroup
                size="small"
                value={language}
                exclusive
                onChange={(_, value) => {
                  if (value) setLanguage(value);
                }}
                aria-label={t('navbar.language')}
                sx={{
                  '& .MuiToggleButton-root': {
                    border: '1px solid var(--surface-border)',
                    color: 'var(--text-subtle)',
                    px: 1.2,
                    textTransform: 'none',
                    fontWeight: 700,
                  },
                  '& .MuiToggleButton-root.Mui-selected': {
                    color: 'var(--brand-accent)',
                    backgroundColor: 'var(--surface-hover)',
                  },
                }}
              >
                <ToggleButton value="en" aria-label={t('navbar.english')}>
                  EN
                </ToggleButton>
                <ToggleButton value="ko" aria-label={t('navbar.korean')}>
                  KO
                </ToggleButton>
              </ToggleButtonGroup>

              <IconButton
                sx={{ display: { xs: 'inline-flex', md: 'none' }, color: 'var(--text-strong)' }}
                onClick={() => setDrawerOpen(true)}
                aria-label={t('navbar.menu')}
              >
                <MenuIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </Paper>
      </Container>

      <Drawer
        anchor="right"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        PaperProps={{
          sx: {
            width: 280,
            p: 1,
            backgroundColor: 'var(--panel-bg)',
          },
        }}
      >
        <List>
          {navItems.map((item) => (
            <ListItemButton
              key={item.key}
              component={NavLink}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setDrawerOpen(false)}
              sx={{
                borderRadius: 2,
                '&.active': {
                  backgroundColor: 'var(--surface-hover)',
                  color: 'var(--brand-accent)',
                },
              }}
            >
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>
      </Drawer>
    </AppBar>
  );
};

export default Navbar;
