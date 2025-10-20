import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Grid,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { fetchProtocols } from '../services/api';
import RiskTrendsChart from './RiskTrendsChart';

const AllProtocolsTrendsGrid: React.FC = () => {
  const { data: protocols, isLoading, error } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" py={10}>
        <CircularProgress size={60} sx={{ color: '#6366f1' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert 
        severity="error"
        sx={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
        }}
      >
        Failed to load protocols. Please refresh the page.
      </Alert>
    );
  }

  if (!protocols || protocols.length === 0) {
    return (
      <Alert 
        severity="info"
        sx={{
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
        }}
      >
        No protocols available for analysis.
      </Alert>
    );
  }

  return (
    <Box>
      <Box mb={4} textAlign="center">
        <Typography
          variant="h4"
          gutterBottom
          sx={{
            background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 700,
            mb: 1,
          }}
        >
          📊 7-Day Risk Trend Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time risk assessment trends for all {protocols.length} monitored protocols
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {protocols.map((protocol: any) => (
          <Grid item xs={12} lg={6} key={protocol.id}>
            <RiskTrendsChart
              protocolId={protocol.id}
              protocolName={protocol.name}
              days={7}
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default AllProtocolsTrendsGrid;


