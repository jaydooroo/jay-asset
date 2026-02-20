import React from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { useLanguage } from '../../i18n/LanguageContext';
import TickerInfoLabel from '../common/TickerInfoLabel';

const ResultsTable = ({ rows, momentumScores, height = null }) => {
  const { t } = useLanguage();
  if (!rows || rows.length === 0) return null;

  const containerSx = height ? { maxHeight: height, overflowX: 'auto' } : { overflowX: 'auto' };

  return (
    <Box>
      <Typography variant="subtitle2" sx={{ fontWeight: 800, mb: 1 }}>
        {t('table.title')}
      </Typography>
      <TableContainer sx={containerSx}>
        <Table size="small" stickyHeader sx={{ width: '100%' }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ width: { xs: '34%', sm: '30%' } }}>
                <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 0.5 }}>
                  {t('table.asset')}
                  <Tooltip title={t('table.tickerHint')} arrow placement="top">
                    <InfoOutlinedIcon sx={{ fontSize: 15, color: 'text.secondary' }} />
                  </Tooltip>
                </Box>
              </TableCell>
              <TableCell align="right" sx={{ width: { xs: '24%', sm: '24%' } }}>
                {t('table.amount')}
              </TableCell>
              <TableCell align="right" sx={{ width: { xs: '18%', sm: '18%' } }}>
                {t('table.percent')}
              </TableCell>
              <TableCell align="right" sx={{ width: { xs: '24%', sm: '28%' } }}>
                {t('table.momentum')}
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.asset}>
                <TableCell
                  sx={{
                    fontWeight: 700,
                    whiteSpace: 'nowrap',
                    overflow: 'visible',
                    py: 1,
                  }}
                >
                  <TickerInfoLabel ticker={row.asset} />
                </TableCell>
                <TableCell align="right" sx={{ whiteSpace: 'nowrap', py: 1 }}>
                  ${Number(row.amount).toLocaleString()}
                </TableCell>
                <TableCell align="right" sx={{ whiteSpace: 'nowrap', py: 1 }}>
                  {Number(row.percentage).toFixed(2)}%
                </TableCell>
                <TableCell align="right" sx={{ whiteSpace: 'nowrap', py: 1 }}>
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
