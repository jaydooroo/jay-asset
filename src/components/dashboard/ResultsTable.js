import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';

const ResultsTable = ({ rows, momentumScores, height = 280 }) => {
  if (!rows || rows.length === 0) return null;

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        Allocation Table
      </Typography>
      <TableContainer sx={{ maxHeight: height }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Asset</TableCell>
              <TableCell align="right">$</TableCell>
              <TableCell align="right">%</TableCell>
              <TableCell align="right">Momentum</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.asset}>
                <TableCell sx={{ fontWeight: 700 }}>{row.asset}</TableCell>
                <TableCell align="right">${Number(row.amount).toLocaleString()}</TableCell>
                <TableCell align="right">{Number(row.percentage).toFixed(2)}%</TableCell>
                <TableCell align="right">
                  {momentumScores && typeof momentumScores[row.asset] === 'number'
                    ? `${(momentumScores[row.asset] * 100).toFixed(2)}%`
                    : '—'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default ResultsTable;
