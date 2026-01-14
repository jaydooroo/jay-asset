import React from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
} from "@mui/material";
import { Link } from "react-router-dom";
import logo from "../assets/logo.png";

const Navbar = () => {
  return (
    <AppBar
      position="sticky"
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
              About
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
              Contact
            </Button>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
