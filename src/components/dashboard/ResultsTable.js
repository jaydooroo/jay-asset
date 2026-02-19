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
import { useLanguage } from '../../i18n/LanguageContext';

const ResultsTable = ({ rows, momentumScores, height = 280 }) => {
  const { t } = useLanguage();
  if (!rows || rows.length === 0) return null;

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        {t('table.title')}
      </Typography>
      <TableContainer sx={{ maxHeight: height }}>
        <Table size="small" stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>{t('table.asset')}</TableCell>
              <TableCell align="right">{t('table.amount')}</TableCell>
              <TableCell align="right">{t('table.percent')}</TableCell>
              <TableCell align="right">{t('table.momentum')}</TableCell>
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
                    : t('table.unknown')}
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
