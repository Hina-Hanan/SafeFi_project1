import React from 'react';
import { Grid, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { fetchProtocols } from '../services/api';
import ProtocolCard from './ProtocolCard';
import { colors } from '../utils/riskColors';
import { ProtocolWithRisk } from '../types';

interface ProtocolHeatmapProps {
  onProtocolSelect: (protocolId: string) => void;
}

export default function ProtocolHeatmap({ onProtocolSelect }: ProtocolHeatmapProps) {
  const { data: protocols, isLoading, error } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
        <CircularProgress size={60} sx={{ color: colors.white }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error"
        sx={{
          background: colors.redDark,
          border: `2px solid ${colors.red}`,
          color: colors.white,
        }}
      >
        Failed to load protocols. Please try again.
      </Alert>
    );
  }

  if (!protocols || protocols.length === 0) {
    return (
      <Alert 
        severity="info"
        sx={{
          background: colors.darkGray,
          border: `2px solid ${colors.gray}`,
          color: colors.white,
        }}
      >
        No protocols available. Please check your database.
      </Alert>
    );
  }

  // Sort protocols by risk score (high to low)
  const sortedProtocols = [...protocols].sort((a, b) => {
    const scoreA = (a.latest_risk?.risk_score || 0) * 100;
    const scoreB = (b.latest_risk?.risk_score || 0) * 100;
    return scoreB - scoreA;
  });

  // Calculate total TVL from all protocols
  const totalTvl = protocols.reduce((sum: number, protocol: ProtocolWithRisk) => {
    const tvl = protocol.latest_metrics?.tvl_usd || 0;
    return sum + tvl;
  }, 0);

  return (
    <Box>
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="h5"
          sx={{
            fontWeight: 700,
            color: colors.white,
            mb: 1,
          }}
        >
          Protocol Risk Heatmap
        </Typography>
        <Typography
          variant="body2"
          sx={{
            color: colors.textGray,
            mb: 2,
          }}
        >
          Click on any protocol card to view detailed risk analysis
        </Typography>
        <Typography
          variant="h6"
          sx={{
            fontWeight: 600,
            color: colors.white,
            mb: 2,
          }}
        >
          Total TVL: ${totalTvl.toLocaleString()}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {sortedProtocols.map((protocol: ProtocolWithRisk) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={protocol.id}>
            <ProtocolCard
              protocol={protocol}
              onClick={() => onProtocolSelect(protocol.id)}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
