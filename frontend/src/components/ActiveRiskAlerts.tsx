import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Alert,
  AlertTitle,
  Chip,
  Grid,
  IconButton,
  Collapse,
  Badge,
  Button,
  Divider,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
} from '@mui/icons-material';
import { fetchProtocols } from '../services/api';

interface ThresholdSettings {
  enabled: boolean;
  highRiskThreshold: number;
  mediumRiskThreshold: number;
  notifyOnHigh: boolean;
  notifyOnMedium: boolean;
}

interface RiskAlert {
  id: string;
  protocolId: string;
  protocolName: string;
  riskScore: number;
  riskLevel: 'high' | 'medium' | 'low';
  severity: 'error' | 'warning' | 'info';
  message: string;
  timestamp: string;
}

const ActiveRiskAlerts: React.FC = () => {
  const [dismissedAlerts, setDismissedAlerts] = useState<string[]>(() => {
    const saved = localStorage.getItem('dismissedAlerts');
    return saved ? JSON.parse(saved) : [];
  });
  const [expanded, setExpanded] = useState(true);

  const [settings, setSettings] = useState<ThresholdSettings>(() => {
    const saved = localStorage.getItem('riskThresholdSettings');
    return saved ? JSON.parse(saved) : {
      enabled: true,
      highRiskThreshold: 70,
      mediumRiskThreshold: 40,
      notifyOnHigh: true,
      notifyOnMedium: true,
    };
  });

  // Listen for settings changes
  useEffect(() => {
    const handleStorageChange = () => {
      const saved = localStorage.getItem('riskThresholdSettings');
      if (saved) {
        setSettings(JSON.parse(saved));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    const interval = setInterval(handleStorageChange, 1000); // Poll every second

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  const { data: protocols } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Generate alerts based on protocols and threshold settings
  const alerts: RiskAlert[] = React.useMemo(() => {
    if (!protocols || !settings.enabled) return [];

    const generatedAlerts: RiskAlert[] = [];

    protocols.forEach((protocol: any) => {
      const riskScore = protocol.latest_risk?.risk_score 
        ? protocol.latest_risk.risk_score * 100 
        : 0;

      let severity: 'error' | 'warning' | 'info' = 'info';
      let riskLevel: 'high' | 'medium' | 'low' = 'low';
      let message = '';

      if (riskScore >= settings.highRiskThreshold && settings.notifyOnHigh) {
        severity = 'error';
        riskLevel = 'high';
        message = `High risk detected! ${protocol.name} has exceeded your risk threshold of ${settings.highRiskThreshold}%`;
      } else if (riskScore >= settings.mediumRiskThreshold && settings.notifyOnMedium) {
        severity = 'warning';
        riskLevel = 'medium';
        message = `Medium risk alert. ${protocol.name} risk score is above ${settings.mediumRiskThreshold}%`;
      }

      if (message) {
        const alertId = `${protocol.id}-${riskLevel}`;
        if (!dismissedAlerts.includes(alertId)) {
          generatedAlerts.push({
            id: alertId,
            protocolId: protocol.id,
            protocolName: protocol.name,
            riskScore,
            riskLevel,
            severity,
            message,
            timestamp: new Date().toISOString(),
          });
        }
      }
    });

    return generatedAlerts.sort((a, b) => b.riskScore - a.riskScore);
  }, [protocols, settings, dismissedAlerts]);

  const handleDismiss = (alertId: string) => {
    const updated = [...dismissedAlerts, alertId];
    setDismissedAlerts(updated);
    localStorage.setItem('dismissedAlerts', JSON.stringify(updated));
  };

  const handleClearAll = () => {
    setDismissedAlerts([]);
    localStorage.setItem('dismissedAlerts', JSON.stringify([]));
  };

  if (!settings.enabled) {
    return (
      <Alert 
        severity="info"
        icon={<InfoIcon />}
        sx={{
          background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(34, 211, 238, 0.1) 100%)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <AlertTitle sx={{ fontWeight: 'bold' }}>Risk Alerts Disabled</AlertTitle>
        Enable risk alerts in the settings below to receive notifications when protocols exceed your risk thresholds.
      </Alert>
    );
  }

  if (alerts.length === 0) {
    return (
      <Alert 
        severity="success"
        icon={<NotificationsIcon />}
        sx={{
          background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          backdropFilter: 'blur(10px)',
        }}
      >
        <AlertTitle sx={{ fontWeight: 'bold' }}>All Clear! ✅</AlertTitle>
        No protocols currently exceed your risk thresholds. All monitored protocols are within acceptable risk levels.
      </Alert>
    );
  }

  const highRiskAlerts = alerts.filter(a => a.severity === 'error');
  const mediumRiskAlerts = alerts.filter(a => a.severity === 'warning');

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)',
        backdropFilter: 'blur(20px)',
        border: '2px solid rgba(239, 68, 68, 0.3)',
        boxShadow: '0 8px 32px rgba(239, 68, 68, 0.3)',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Box display="flex" alignItems="center" gap={2}>
            <Badge badgeContent={alerts.length} color="error">
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 20px rgba(239, 68, 68, 0.4)',
                  animation: 'pulse 2s ease-in-out infinite',
                  '@keyframes pulse': {
                    '0%, 100%': { boxShadow: '0 4px 20px rgba(239, 68, 68, 0.4)' },
                    '50%': { boxShadow: '0 4px 30px rgba(239, 68, 68, 0.8)' },
                  },
                }}
              >
                <NotificationsActiveIcon sx={{ color: 'white', fontSize: '1.5rem' }} />
              </Box>
            </Badge>
            <Box>
              <Typography 
                variant="h6" 
                fontWeight="bold"
                sx={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #f59e0b 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Active Risk Alerts
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {highRiskAlerts.length} high risk, {mediumRiskAlerts.length} medium risk
              </Typography>
            </Box>
          </Box>
          <Box display="flex" gap={1}>
            {alerts.length > 0 && (
              <Button
                size="small"
                variant="outlined"
                onClick={handleClearAll}
                sx={{
                  borderColor: 'rgba(239, 68, 68, 0.5)',
                  color: '#ef4444',
                  '&:hover': {
                    borderColor: '#ef4444',
                    background: 'rgba(239, 68, 68, 0.1)',
                  },
                }}
              >
                Clear All
              </Button>
            )}
            <IconButton 
              onClick={() => setExpanded(!expanded)}
              sx={{
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                '&:hover': {
                  background: 'rgba(239, 68, 68, 0.2)',
                },
              }}
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Collapse in={expanded}>
          <Grid container spacing={2}>
            {alerts.map((alert) => (
              <Grid item xs={12} key={alert.id}>
                <Alert
                  severity={alert.severity}
                  icon={alert.severity === 'error' ? <ErrorIcon /> : <WarningIcon />}
                  action={
                    <IconButton
                      size="small"
                      onClick={() => handleDismiss(alert.id)}
                      sx={{ color: 'inherit' }}
                    >
                      <CloseIcon fontSize="small" />
                    </IconButton>
                  }
                  sx={{
                    background: alert.severity === 'error'
                      ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(248, 113, 113, 0.15) 100%)'
                      : 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.15) 100%)',
                    border: `2px solid ${alert.severity === 'error' ? '#ef4444' : '#f59e0b'}`,
                    backdropFilter: 'blur(10px)',
                    '& .MuiAlert-icon': {
                      fontSize: '1.5rem',
                    },
                  }}
                >
                  <AlertTitle sx={{ fontWeight: 'bold', mb: 1 }}>
                    {alert.protocolName}
                    <Chip
                      label={`${alert.riskScore.toFixed(0)}%`}
                      size="small"
                      sx={{
                        ml: 2,
                        background: alert.severity === 'error' ? '#ef4444' : '#f59e0b',
                        color: 'white',
                        fontWeight: 'bold',
                      }}
                    />
                  </AlertTitle>
                  <Typography variant="body2">
                    {alert.message}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                    Detected: {new Date(alert.timestamp).toLocaleString()}
                  </Typography>
                </Alert>
              </Grid>
            ))}
          </Grid>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default ActiveRiskAlerts;





















