import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  ToggleButton,
  ToggleButtonGroup,
} from "@mui/material";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";
import { useLanguage } from "../i18n/LanguageContext";

// Top navigation bar shown across the app.
// Uses react-router's <Link> so navigation stays inside the SPA (no page reload).
const Navbar = () => {
  const { language, setLanguage, t } = useLanguage();

  return (
    <AppBar
      // Use "static" so the navbar scrolls with the page (not floating/sticky).
      position="static"
      sx={{
        backgroundColor: "var(--bg-primary)",
        color: "var(--text-primary)",
        boxShadow: "0 4px 12px var(--shadow-color)",
      }}
    >
      <Container maxWidth="lg">
        <Toolbar sx={{ py: 1 }}>
          <Box
            component={Link}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: "none",
              display: "flex",
              alignItems: "center",
              gap: 1,
            }}
          >
            <img
              src={logo}
              alt="Logo"
              style={{
                height: "40px",
                width: "auto",
              }}
            />
            <Typography
              variant="h6"
              sx={{
                color: "var(--text-primary)",
                fontWeight: "bold",
                "&:hover": {
                  color: "var(--accent-primary)",
                },
              }}
            >
              Jehyeon Lee
            </Typography>
          </Box>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <ToggleButtonGroup
              size="small"
              value={language}
              exclusive
              onChange={(_, value) => {
                if (value) setLanguage(value);
              }}
              aria-label={t("navbar.language")}
            >
              <ToggleButton value="en" aria-label={t("navbar.english")}>
                EN
              </ToggleButton>
              <ToggleButton value="ko" aria-label={t("navbar.korean")}>
                KO
              </ToggleButton>
            </ToggleButtonGroup>
            {/* Note: /about and /contact routes are not currently defined in src/App.js */}
            <Button
              component={Link}
              to="/about"
              sx={{
                color: "var(--text-primary)",
                "&:hover": {
                  color: "var(--accent-primary)",
                  backgroundColor: "var(--hover-bg)",
                },
              }}
            >
              {t("navbar.about")}
            </Button>
            <Button
              component={Link}
              to="/contact"
              sx={{
                color: "var(--text-primary)",
                "&:hover": {
                  color: "var(--accent-primary)",
                  backgroundColor: "var(--hover-bg)",
                },
              }}
            >
              {t("navbar.contact")}
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
