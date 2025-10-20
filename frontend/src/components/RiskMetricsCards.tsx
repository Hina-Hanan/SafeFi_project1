import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Security,
  Timeline,
  Warning,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth, fetchProtocols } from '../services/api';
import { getRiskColor, getStatusColor, colors } from '../utils/riskColors';

interface RiskMetricsCardsProps {
  selectedProtocolId?: string;
}

export default function RiskMetricsCards({ selectedProtocolId }: RiskMetricsCardsProps) {
  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  });

  const { data: protocols } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  });

  const getRiskDistribution = () => {
    if (!protocols || protocols.length === 0) {
      return { low: 0, medium: 0, high: 0, total: 0 };
    }
    
    const counts = { low: 0, medium: 0, high: 0 };
    
    protocols.forEach((protocol: any) => {
      const riskLevel = protocol.latest_risk?.risk_level || 'low';
      if (riskLevel === 'low') counts.low++;
      else if (riskLevel === 'medium') counts.medium++;
      else if (riskLevel === 'high') counts.high++;
    });
    
    return {
      ...counts,
      total: protocols.length,
    };
  };

  const getSystemStatus = () => {
    if (!health) return { status: 'UNKNOWN', isHealthy: false };
    const isHealthy = health.database_connected;
    return {
      status: isHealthy ? 'ONLINE' : 'OFFLINE',
      isHealthy,
    };
  };

  const riskDistribution = getRiskDistribution();
  const systemStatus = getSystemStatus();

  const metrics = [
    {
      title: 'System Status',
      value: systemStatus.status,
      icon: <Security sx={{ fontSize: 40, color: systemStatus.isHealthy ? colors.green : colors.red }} />,
      bgColor: getStatusColor(systemStatus.isHealthy, 'background'),
      borderColor: getStatusColor(systemStatus.isHealthy, 'border'),
      subtitle: health ? 
        `Database: ${health.database_connected ? 'Connected' : 'Disconnected'}` :
        'Checking...',
      loading: healthLoading,
    },
    {
      title: 'Total Protocols',
      value: riskDistribution.total.toString(),
      icon: <Timeline sx={{ fontSize: 40, color: colors.white }} />,
      bgColor: colors.darkGray,
      borderColor: colors.gray,
      subtitle: 'Active monitoring',
      loading: false,
    },
    {
      title: 'High Risk',
      value: riskDistribution.high.toString(),
      icon: <Warning sx={{ fontSize: 40, color: colors.red }} />,
      bgColor: getRiskColor('high', 'background'),
      borderColor: getRiskColor('high', 'border'),
      subtitle: `${riskDistribution.high} protocols need attention`,
      loading: false,
    },
    {
      title: 'Risk Distribution',
      value: `${riskDistribution.low}/${riskDistribution.medium}/${riskDistribution.high}`,
      icon: <TrendingUp sx={{ fontSize: 40, color: colors.white }} />,
      bgColor: colors.darkGray,
      borderColor: colors.gray,
      subtitle: 'Low / Medium / High',
      loading: false,
    },
  ];

  return (
    <Grid container spacing={3}>
      {metrics.map((metric, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Card
            sx={{
              background: metric.bgColor,
              border: `2px solid ${metric.borderColor}`,
              height: '100%',
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 700,
                    color: colors.white,
                    fontSize: '1rem',
                  }}
                >
                  {metric.title}
                </Typography>
                {metric.icon}
              </Box>

              {metric.loading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
                  <CircularProgress size={40} sx={{ color: colors.white }} />
                </Box>
              ) : (
                <>
                  <Typography
                    variant="h3"
                    sx={{
                      fontWeight: 700,
                      color: colors.white,
                      mb: 1,
                    }}
                  >
                    {metric.value}
                  </Typography>
                  <Typography
                    variant="body2"
                    sx={{
                      color: colors.textGray,
                      fontWeight: 600,
                    }}
                  >
                    {metric.subtitle}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}

      {/* Risk Level Legend */}
      <Grid item xs={12}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
          <Chip
            label="Low Risk"
            sx={{
              background: getRiskColor('low', 'background'),
              border: `2px solid ${getRiskColor('low', 'border')}`,
              color: getRiskColor('low', 'text'),
              fontWeight: 600,
            }}
          />
          <Chip
            label="Medium Risk"
            sx={{
              background: getRiskColor('medium', 'background'),
              border: `2px solid ${getRiskColor('medium', 'border')}`,
              color: getRiskColor('medium', 'text'),
              fontWeight: 600,
            }}
          />
          <Chip
            label="High Risk"
            sx={{
              background: getRiskColor('high', 'background'),
              border: `2px solid ${getRiskColor('high', 'border')}`,
              color: getRiskColor('high', 'text'),
              fontWeight: 600,
            }}
          />
        </Box>
      </Grid>
    </Grid>
  );
}
