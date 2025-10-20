import React from 'react';
import { Card, CardContent, Typography, Chip, Box } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import { getRiskColor, getRiskColorByScore, colors } from '../utils/riskColors';

interface ProtocolCardProps {
  protocol: any;
  onClick: () => void;
}

export default function ProtocolCard({ protocol, onClick }: ProtocolCardProps) {
  const riskScore = (protocol.latest_risk?.risk_score || 0) * 100;
  const riskLevel = protocol.latest_risk?.risk_level || 'unknown';
  const tvl = protocol.latest_metric?.tvl || 0;
  
  // Format large numbers
  const formatLargeNumber = (num: number) => {
    if (num >= 1_000_000_000) return `$${(num / 1_000_000_000).toFixed(2)}B`;
    if (num >= 1_000_000) return `$${(num / 1_000_000).toFixed(2)}M`;
    if (num >= 1_000) return `$${(num / 1_000).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  };

  // Get trend icon
  const getTrendIcon = () => {
    const trend = protocol.latest_risk?.trend || 0;
    if (trend > 0) return <TrendingUp sx={{ color: colors.red, fontSize: 20 }} />;
    if (trend < 0) return <TrendingDown sx={{ color: colors.green, fontSize: 20 }} />;
    return <Remove sx={{ color: colors.textGray, fontSize: 20 }} />;
  };

  const bgColor = getRiskColorByScore(riskScore, 'background');
  const borderColor = getRiskColorByScore(riskScore, 'border');

  return (
    <Card
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: 'pointer',
        background: bgColor,
        border: `3px solid ${borderColor}`,
        transition: 'transform 0.2s',
        '&:hover': {
          transform: 'translateY(-4px)',
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              color: colors.white,
              fontSize: '1.1rem',
            }}
          >
            {protocol.name || 'Unknown'}
          </Typography>
          {getTrendIcon()}
        </Box>

        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ color: colors.textGray, mb: 0.5 }}>
            Risk Score
          </Typography>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              color: colors.white,
            }}
          >
            {riskScore.toFixed(1)}
          </Typography>
        </Box>

        <Box sx={{ mb: 2 }}>
          <Chip
            label={riskLevel.toUpperCase()}
            size="small"
            sx={{
              background: getRiskColor(riskLevel, 'background'),
              border: `2px solid ${getRiskColor(riskLevel, 'border')}`,
              color: getRiskColor(riskLevel, 'text'),
              fontWeight: 700,
            }}
          />
        </Box>

        {tvl > 0 && (
          <Box>
            <Typography variant="body2" sx={{ color: colors.textGray, mb: 0.5 }}>
              Total Value Locked
            </Typography>
            <Typography
              variant="body1"
              sx={{
                fontWeight: 600,
                color: colors.white,
              }}
            >
              {formatLargeNumber(tvl)}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
