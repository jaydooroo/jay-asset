import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Container,
  Grid,
  Paper,
  Divider,
} from '@mui/material';
import CalculateIcon from '@mui/icons-material/Calculate';
import './AssetCalculator.css';

const strategies = {
  conservative: {
    name: 'Conservative',
    description: 'Low risk, stable returns',
    allocation: {
      'Bonds': 60,
      'Stocks': 20,
      'Cash': 15,
      'Real Estate': 5,
    }
  },
  balanced: {
    name: 'Balanced',
    description: 'Moderate risk, balanced growth',
    allocation: {
      'Stocks': 40,
      'Bonds': 30,
      'Real Estate': 15,
      'Commodities': 10,
      'Cash': 5,
    }
  },
  aggressive: {
    name: 'Aggressive',
    description: 'High risk, maximum growth potential',
    allocation: {
      'Stocks': 70,
      'Real Estate': 15,
      'Commodities': 10,
      'Bonds': 5,
    }
  },
  growth: {
    name: 'Growth',
    description: 'Focus on capital appreciation',
    allocation: {
      'Stocks': 60,
      'Real Estate': 20,
      'Bonds': 10,
      'Commodities': 10,
    }
  },
  income: {
    name: 'Income',
    description: 'Focus on generating regular income',
    allocation: {
      'Bonds': 50,
      'Dividend Stocks': 25,
      'Real Estate': 15,
      'Cash': 10,
    }
  },
};

const AssetCalculator = () => {
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [amount, setAmount] = useState('');
  const [results, setResults] = useState(null);

  const handleCalculate = () => {
    if (!selectedStrategy || !amount || amount <= 0) {
      alert('Please select a strategy and enter a valid amount');
      return;
    }

    const strategy = strategies[selectedStrategy];
    const totalAmount = parseFloat(amount);

    const calculations = Object.entries(strategy.allocation).map(([asset, percentage]) => ({
      asset,
      percentage,
      amount: (totalAmount * percentage / 100).toFixed(2),
    }));

    setResults({
      strategy: strategy.name,
      description: strategy.description,
      totalAmount: totalAmount.toFixed(2),
      breakdown: calculations,
    });
  };

  const handleReset = () => {
    setSelectedStrategy('');
    setAmount('');
    setResults(null);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Card elevation={3} className="calculator-card">
        <CardContent>
          <Typography variant="h4" component="h1" gutterBottom align="center" sx={{ mb: 3, fontWeight: 'bold' }}>
            Asset Allocation Calculator
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
            Select an investment strategy and enter your amount to see how to allocate your assets
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="strategy-label">Investment Strategy</InputLabel>
                <Select
                  labelId="strategy-label"
                  value={selectedStrategy}
                  label="Investment Strategy"
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                >
                  {Object.entries(strategies).map(([key, strategy]) => (
                    <MenuItem key={key} value={key}>
                      <Box>
                        <Typography variant="body1">{strategy.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {strategy.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Investment Amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount in $"
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  size="large"
                  startIcon={<CalculateIcon />}
                  onClick={handleCalculate}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                  }}
                >
                  Calculate
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleReset}
                  sx={{
                    px: 4,
                    py: 1.5,
                    fontSize: '1.1rem',
                  }}
                >
                  Reset
                </Button>
              </Box>
            </Grid>
          </Grid>

          {results && (
            <Box sx={{ mt: 4 }}>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h5" gutterBottom align="center" sx={{ mb: 3, fontWeight: 'bold' }}>
                Your Asset Allocation
              </Typography>

              <Paper elevation={2} sx={{ p: 3, mb: 3, backgroundColor: '#f5f5f5' }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">Strategy</Typography>
                    <Typography variant="h6">{results.strategy}</Typography>
                  </Grid>
                  <Grid item xs={12} sm={8}>
                    <Typography variant="body2" color="text.secondary">Description</Typography>
                    <Typography variant="body1">{results.description}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Total Investment</Typography>
                    <Typography variant="h5" color="primary">
                      ${parseFloat(results.totalAmount).toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>
              </Paper>

              <Grid container spacing={2}>
                {results.breakdown.map((item, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Card variant="outlined" className="allocation-card">
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          {item.asset}
                        </Typography>
                        <Typography variant="h4" color="primary" sx={{ my: 1 }}>
                          ${parseFloat(item.amount).toLocaleString()}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {item.percentage}% of total
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default AssetCalculator;
