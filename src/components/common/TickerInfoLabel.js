import React, { useMemo, useState } from 'react';
import {
  Box,
  ButtonBase,
  Popover,
  Tooltip,
  Typography,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import { getTickerMetadata } from '../../data/tickerMetadata';
import { useLanguage } from '../../i18n/LanguageContext';

const TickerInfoLabel = ({ ticker, fontWeight = 700, size = 'body2', showIcon = true }) => {
  const { t } = useLanguage();
  const theme = useTheme();
  const isTouchLayout = useMediaQuery(theme.breakpoints.down('sm'));
  const [anchorEl, setAnchorEl] = useState(null);

  const metadata = useMemo(() => getTickerMetadata(ticker), [ticker]);

  const infoContent = (
    <Box sx={{ maxWidth: 260 }}>
      <Typography sx={{ fontWeight: 800, fontSize: '0.88rem', mb: 0.4, color: 'var(--text-strong)' }}>
        {metadata.name}
      </Typography>
      <Typography sx={{ fontSize: '0.79rem', color: 'var(--text-subtle)' }}>
        {t('ticker.assetType', { value: metadata.assetType })}
      </Typography>
      <Typography sx={{ fontSize: '0.79rem', color: 'var(--text-subtle)' }}>
        {t('ticker.market', { value: metadata.market })}
      </Typography>
      <Typography sx={{ fontSize: '0.79rem', color: 'var(--text-subtle)' }}>
        {t('ticker.role', { value: metadata.role })}
      </Typography>
    </Box>
  );

  const trigger = (
    <ButtonBase
      onClick={(event) => {
        if (isTouchLayout) setAnchorEl(event.currentTarget);
      }}
      sx={{
        borderRadius: 1,
        display: 'inline-flex',
        alignItems: 'center',
        gap: showIcon ? 0.35 : 0,
        minWidth: 0,
        px: 0.25,
        cursor: 'help',
      }}
      aria-label={t('ticker.moreInfo')}
    >
      <Typography
        variant={size}
        sx={{
          fontWeight,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
        }}
      >
        {metadata.ticker}
      </Typography>
      {showIcon && <InfoOutlinedIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
    </ButtonBase>
  );

  if (isTouchLayout) {
    return (
      <>
        {trigger}
        <Popover
          open={Boolean(anchorEl)}
          anchorEl={anchorEl}
          onClose={() => setAnchorEl(null)}
          disableScrollLock
          anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
          transformOrigin={{ vertical: 'top', horizontal: 'left' }}
          PaperProps={{
            sx: {
              border: '1px solid var(--surface-border)',
              boxShadow: '0 12px 28px rgba(15, 23, 42, 0.16)',
              backgroundColor: 'rgba(255, 255, 255, 0.98)',
            },
          }}
        >
          <Box sx={{ p: 1.25 }}>{infoContent}</Box>
        </Popover>
      </>
    );
  }

  return (
    <Tooltip
      title={infoContent}
      arrow
      placement="top"
      enterDelay={120}
      slotProps={{
        tooltip: {
          sx: {
            backgroundColor: 'rgba(255, 255, 255, 0.98)',
            border: '1px solid var(--surface-border)',
            boxShadow: '0 12px 28px rgba(15, 23, 42, 0.16)',
            p: 1.1,
            maxWidth: 280,
          },
        },
        arrow: {
          sx: {
            color: 'rgba(255, 255, 255, 0.98)',
          },
        },
      }}
    >
      <Box component="span">{trigger}</Box>
    </Tooltip>
  );
};

export default TickerInfoLabel;
