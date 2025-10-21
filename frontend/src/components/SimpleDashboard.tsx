import React, { useState } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Chip,
  Alert,
  Tabs,
  Tab,
  Paper,
  Badge,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { fetchProtocols, fetchHealth } from '../services/api';
import RiskMetricsCards from './RiskMetricsCards';
import ProtocolHeatmap from './ProtocolHeatmap';
import AllProtocolsTrendsGrid from './AllProtocolsTrendsGrid';
import RiskThresholdSettings from './RiskThresholdSettings';
import ActiveRiskAlerts from './ActiveRiskAlerts';
import PortfolioAnalyzer from './PortfolioAnalyzer';
import AIAssistantChat from './AIAssistantChat';
import EmailSubscription from './EmailSubscription';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export default function SimpleDashboard() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedProtocolId, setSelectedProtocolId] = useState<string>('');
  const [selectedProtocolName, setSelectedProtocolName] = useState<string>('');

  const { data: protocols, refetch: refetchProtocols } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  });

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  });

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleProtocolSelect = (protocolId: string) => {
    const protocol = protocols?.find((p: any) => p.id === protocolId);
    setSelectedProtocolId(protocolId);
    setSelectedProtocolName(protocol?.name || '');
    setSelectedTab(1); // Switch to analysis tab
  };

  const handleRefresh = () => {
    refetchProtocols();
  };

  const getSystemStatus = () => {
    if (!health) return { status: 'checking', color: '#666666', bgColor: '#0A0A0A', textColor: '#AAAAAA' };
    const isHealthy = health.database_connected;
    return {
      status: isHealthy ? 'ONLINE' : 'OFFLINE',
      color: isHealthy ? '#00CC00' : '#FF0000',
      bgColor: isHealthy ? '#001A00' : '#1A0000',
      textColor: isHealthy ? '#00CC00' : '#FF0000',
    };
  };

  const systemStatus = getSystemStatus();

  // Count active alerts
  const activeAlerts = React.useMemo(() => {
    if (!protocols) return 0;
    const settings = localStorage.getItem('riskThresholdSettings');
    const thresholds = settings ? JSON.parse(settings) : { highRiskThreshold: 70, mediumRiskThreshold: 40, enabled: true };
    
    if (!thresholds.enabled) return 0;

    return protocols.filter((p: any) => {
      const score = (p.latest_risk?.risk_score || 0) * 100;
      return score >= thresholds.mediumRiskThreshold;
    }).length;
  }, [protocols]);

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh', background: '#000000' }}>
      {/* Header */}
      <AppBar
        position="static"
        elevation={0}
        sx={{
          background: '#000000',
          borderBottom: '2px solid #222222',
        }}
      >
        <Toolbar sx={{ py: 1 }}>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                background: '#0A0A0A',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px solid #333333',
              }}
            >
              <Typography variant="h6" fontWeight="bold" sx={{ color: '#FFFFFF', fontSize: '1.8rem' }}>
                ₿
              </Typography>
            </Box>
            <Box>
              <Typography
                variant="h6"
                component="div"
                sx={{
                  fontWeight: 700,
                  color: '#FFFFFF',
                  fontSize: '1.3rem',
                }}
              >
                SafeFi — DeFi Risk Assessment
              </Typography>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: '#AAAAAA',
                  display: 'block', 
                  mt: -0.5,
                  fontSize: '0.85rem',
                }}
              >
                Real-time protocol risk monitoring
              </Typography>
            </Box>
          </Box>
          
          <Chip
            label={systemStatus.status}
            size="small"
            sx={{
              mr: 2,
              fontWeight: 700,
              background: systemStatus.bgColor,
              border: `2px solid ${systemStatus.color}`,
              color: systemStatus.textColor,
            }}
          />
          
          <Badge badgeContent={activeAlerts} sx={{ 
            mr: 1,
            '& .MuiBadge-badge': {
              background: '#FF0000',
              color: '#FFFFFF',
            }
          }}>
            <IconButton
              sx={{
                background: activeAlerts > 0 ? '#1A0000' : '#0A0A0A',
                border: '2px solid #333333',
                '&:hover': {
                  background: activeAlerts > 0 ? '#330000' : '#1A1A1A',
                },
              }}
            >
              <NotificationsIcon sx={{ color: activeAlerts > 0 ? '#FF0000' : '#FFFFFF' }} />
            </IconButton>
          </Badge>
          
          <IconButton
            onClick={handleRefresh}
            sx={{
              mr: 1,
              background: '#0A0A0A',
              border: '2px solid #333333',
              '&:hover': {
                background: '#1A1A1A',
              },
            }}
          >
            <RefreshIcon sx={{ color: '#FFFFFF' }} />
          </IconButton>
          
          <IconButton
            sx={{
              background: '#0A0A0A',
              border: '2px solid #333333',
              '&:hover': {
                background: '#1A1A1A',
              },
            }}
          >
            <SettingsIcon sx={{ color: '#FFFFFF' }} />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, pb: 4 }}>
        {/* System Status Alerts */}
        {health && !health.database_connected && (
          <Alert
            severity="error"
            sx={{
              mb: 2,
              background: '#1A0000',
              border: '2px solid #FF0000',
              color: '#FFFFFF',
            }}
          >
            ⚠️ Database connection lost. Data may not be up-to-date.
          </Alert>
        )}

        {/* Risk Metrics Overview */}
        <Box mb={4}>
          <RiskMetricsCards selectedProtocolId={selectedProtocolId} />
        </Box>

        {/* Active Alerts Section */}
        <Box mb={4}>
          <ActiveRiskAlerts />
        </Box>

        {/* Alert Settings */}
        <Box mb={4}>
          <RiskThresholdSettings />
        </Box>

        {/* Main Content Tabs */}
        <Paper
          sx={{
            width: '100%',
            background: '#0A0A0A',
            border: '2px solid #222222',
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              borderBottom: '2px solid #222222',
              background: '#000000',
            }}
          >
            <Tabs
              value={selectedTab}
              onChange={handleTabChange}
              aria-label="dashboard tabs"
              sx={{
                '& .MuiTabs-indicator': {
                  background: '#FFFFFF',
                  height: 2,
                },
              }}
            >
              <Tab label="🔥 Risk Heatmap" sx={{ fontWeight: 600 }} />
              <Tab label="📊 7-Day Analysis" sx={{ fontWeight: 600 }} />
              <Tab label="💼 Portfolio" sx={{ fontWeight: 600 }} />
              <Tab label="📧 Email Alerts" sx={{ fontWeight: 600 }} />
              <Tab label="🤖 AI Assistant" sx={{ fontWeight: 600 }} />
            </Tabs>
          </Box>

          <TabPanel value={selectedTab} index={0}>
            <ProtocolHeatmap onProtocolSelect={handleProtocolSelect} />
          </TabPanel>

          <TabPanel value={selectedTab} index={1}>
            <AllProtocolsTrendsGrid />
          </TabPanel>

          <TabPanel value={selectedTab} index={2}>
            <PortfolioAnalyzer />
          </TabPanel>

          <TabPanel value={selectedTab} index={3}>
            <EmailSubscription />
          </TabPanel>

          <TabPanel value={selectedTab} index={4}>
            <AIAssistantChat />
          </TabPanel>
        </Paper>

        {/* Footer */}
        <Box
          mt={6}
          py={4}
          textAlign="center"
          sx={{
            borderTop: '2px solid #222222',
            background: '#0A0A0A',
          }}
        >
          <Typography 
            variant="body2" 
            sx={{
              color: '#FFFFFF',
              fontWeight: 600,
            }}
          >
            DeFi Risk Monitor • Last updated: {new Date().toLocaleString()}
          </Typography>
          {health && (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 2, 
                mt: 2,
                flexWrap: 'wrap',
              }}
            >
              <Chip 
                label={`${health.total_protocols || 0} Protocols`}
                size="small"
                sx={{
                  background: '#0A0A0A',
                  border: '2px solid #666666',
                  fontWeight: 600,
                  color: '#FFFFFF',
                }}
              />
              <Chip 
                label={`$${(health.total_tvl_usd || 0).toLocaleString()} Total TVL`}
                size="small"
                sx={{
                  background: '#0A0A0A',
                  border: '2px solid #666666',
                  fontWeight: 600,
                  color: '#FFFFFF',
                }}
              />
              <Chip 
                label={`${health.total_risk_scores || 0} Risk Assessments`}
                size="small"
                sx={{
                  background: '#0A0A0A',
                  border: '2px solid #666666',
                  fontWeight: 600,
                  color: '#FFFFFF',
                }}
              />
              <Chip 
                label={activeAlerts > 0 ? `${activeAlerts} Active Alerts` : 'No Active Alerts'}
                size="small"
                sx={{
                  background: activeAlerts > 0 ? '#1A0000' : '#001A00',
                  border: activeAlerts > 0 ? '2px solid #FF0000' : '2px solid #00CC00',
                  fontWeight: 600,
                  color: activeAlerts > 0 ? '#FF0000' : '#00CC00',
                }}
              />
            </Box>
          )}
        </Box>
      </Container>
    </Box>
  );
}
