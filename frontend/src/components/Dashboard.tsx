import React, { useState } from 'react'
import {
  Grid,
  Stack,
  Typography,
  Box,
  Tabs,
  Tab,
  Paper,
  Container,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Alert,
} from '@mui/material'
import { Refresh, Settings, Notifications } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { fetchProtocols, fetchHealth } from '../services/api'
import ProtocolHeatmap from './ProtocolHeatmap'
import RiskMetricsCards from './RiskMetricsCards'
import RiskChart from './RiskChart'
import ModelMetrics from './ModelMetrics'
import PortfolioAnalyzer from './PortfolioAnalyzer'
import AlertManager from './AlertManager'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`dashboard-tabpanel-${index}`}
      aria-labelledby={`dashboard-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function Dashboard() {
  const [selectedTab, setSelectedTab] = useState(0)
  const [selectedProtocolId, setSelectedProtocolId] = useState<string>('')

  const { data: protocols, isLoading: protocolsLoading } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 10000,
  })

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue)
  }

  const handleProtocolSelect = (protocolId: string) => {
    setSelectedProtocolId(protocolId)
    setSelectedTab(1) // Switch to risk analysis tab
  }

  const getSystemStatus = () => {
    if (!health) return { status: 'unknown', color: 'default' }
    const isHealthy = health.database_connected && health.mlflow_connected
    return {
      status: isHealthy ? 'healthy' : 'degraded',
      color: isHealthy ? 'success' : 'warning',
    }
  }

  const systemStatus = getSystemStatus()

  return (
    <Box sx={{ flexGrow: 1, minHeight: '100vh' }}>
      {/* Header */}
      <AppBar 
        position="static" 
        color="default" 
        elevation={0}
        sx={{
          background: 'rgba(15, 23, 42, 0.95)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(99, 102, 241, 0.3)',
          boxShadow: '0 4px 24px rgba(99, 102, 241, 0.2)',
        }}
      >
        <Toolbar sx={{ py: 1 }}>
          <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)',
                animation: 'pulse 2s ease-in-out infinite',
                '@keyframes pulse': {
                  '0%, 100%': { boxShadow: '0 0 20px rgba(99, 102, 241, 0.5)' },
                  '50%': { boxShadow: '0 0 30px rgba(99, 102, 241, 0.8)' },
                },
              }}
            >
              <Typography variant="h6" fontWeight="bold" sx={{ color: 'white' }}>
                ₿
              </Typography>
            </Box>
            <Box>
              <Typography 
                variant="h6" 
                component="div" 
                sx={{ 
                  background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                }}
              >
                DeFi Risk Assessment
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', mt: -0.5 }}>
                Real-time Protocol Analysis
              </Typography>
            </Box>
          </Box>
          <Chip
            label={systemStatus.status.toUpperCase()}
            color={systemStatus.color as any}
            size="small"
            sx={{ 
              mr: 2,
              fontWeight: 700,
              background: systemStatus.color === 'success' 
                ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
                : 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
              boxShadow: systemStatus.color === 'success'
                ? '0 0 20px rgba(16, 185, 129, 0.4)'
                : '0 0 20px rgba(245, 158, 11, 0.4)',
            }}
          />
          <IconButton 
            sx={{ 
              mr: 1,
              '&:hover': {
                background: 'rgba(236, 72, 153, 0.2)',
                boxShadow: '0 0 20px rgba(236, 72, 153, 0.4)',
              }
            }}
          >
            <Notifications sx={{ color: '#ec4899' }} />
          </IconButton>
          <IconButton 
            sx={{ 
              mr: 1,
              '&:hover': {
                background: 'rgba(99, 102, 241, 0.2)',
                boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)',
              }
            }}
          >
            <Settings sx={{ color: '#6366f1' }} />
          </IconButton>
          <IconButton
            sx={{
              '&:hover': {
                background: 'rgba(6, 182, 212, 0.2)',
                boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)',
              }
            }}
          >
            <Refresh sx={{ color: '#06b6d4' }} />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4 }}>
        {/* System Status Alert */}
        {health && !health.database_connected && (
          <Alert 
            severity="warning" 
            sx={{ 
              mb: 2,
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 16px rgba(245, 158, 11, 0.2)',
            }}
          >
            Database connection issues detected. Some features may be limited.
          </Alert>
        )}
        {health && !health.mlflow_connected && (
          <Alert 
            severity="warning" 
            sx={{ 
              mb: 2,
              background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(251, 191, 36, 0.1) 100%)',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 16px rgba(245, 158, 11, 0.2)',
            }}
          >
            MLflow connection issues detected. Model training may be unavailable.
          </Alert>
        )}

        {/* Risk Metrics Overview */}
        <Box mb={4}>
          <RiskMetricsCards selectedProtocolId={selectedProtocolId} />
        </Box>

        {/* Main Dashboard Tabs */}
        <Paper 
          sx={{ 
            width: '100%',
            background: 'rgba(15, 23, 42, 0.6)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
            overflow: 'hidden',
          }}
        >
          <Box 
            sx={{ 
              borderBottom: '1px solid rgba(99, 102, 241, 0.2)',
              background: 'linear-gradient(90deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)',
            }}
          >
            <Tabs 
              value={selectedTab} 
              onChange={handleTabChange} 
              aria-label="dashboard tabs"
              sx={{
                '& .MuiTabs-indicator': {
                  background: 'linear-gradient(90deg, #6366f1 0%, #ec4899 100%)',
                  height: 3,
                  borderRadius: '3px 3px 0 0',
                  boxShadow: '0 0 10px rgba(99, 102, 241, 0.6)',
                },
              }}
            >
              <Tab label="🔥 Protocol Heatmap" />
              <Tab label="📊 Risk Analysis" />
              <Tab label="🤖 ML Models" />
              <Tab label="💼 Portfolio Analyzer" />
              <Tab label="🔔 Alerts" />
            </Tabs>
          </Box>

          <TabPanel value={selectedTab} index={0}>
            <ProtocolHeatmap onProtocolSelect={handleProtocolSelect} />
          </TabPanel>

          <TabPanel value={selectedTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                {selectedProtocolId ? (
                  <RiskChart 
                    protocolId={selectedProtocolId} 
                    protocolName={protocols?.find((p: any) => 
                      (p.protocol?.id || p.id) === selectedProtocolId
                    )?.protocol?.name || protocols?.find((p: any) => 
                      (p.protocol?.id || p.id) === selectedProtocolId
                    )?.name}
                  />
                ) : (
                  <Box 
                    textAlign="center" 
                    py={8}
                    sx={{
                      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)',
                      borderRadius: 4,
                      border: '2px dashed rgba(99, 102, 241, 0.3)',
                    }}
                  >
                    <Typography 
                      variant="h5" 
                      gutterBottom
                      sx={{
                        background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                        backgroundClip: 'text',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontWeight: 700,
                      }}
                    >
                      Select a protocol from the heatmap
                    </Typography>
                    <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
                      Click on any protocol card in the heatmap above to see its risk trends and breakdown
                    </Typography>
                  </Box>
                )}
              </Grid>
            </Grid>
          </TabPanel>

          <TabPanel value={selectedTab} index={2}>
            <ModelMetrics />
          </TabPanel>

          <TabPanel value={selectedTab} index={3}>
            <PortfolioAnalyzer />
          </TabPanel>

          <TabPanel value={selectedTab} index={4}>
            <AlertManager />
          </TabPanel>
        </Paper>

        {/* Footer */}
        <Box 
          mt={6} 
          py={4} 
          textAlign="center"
          sx={{
            borderTop: '1px solid rgba(99, 102, 241, 0.2)',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.03) 0%, rgba(236, 72, 153, 0.03) 100%)',
            backdropFilter: 'blur(10px)',
            borderRadius: 2,
            mb: 3,
          }}
        >
          <Typography 
            variant="body2" 
            sx={{
              color: 'text.secondary',
              fontWeight: 500,
            }}
          >
            DeFi Risk Assessment System • Last updated: {new Date().toLocaleString()}
          </Typography>
          {health && (
            <Box 
              sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                gap: 3, 
                mt: 2,
                flexWrap: 'wrap',
              }}
            >
              <Chip 
                label={`${health.total_protocols} Protocols`}
                size="small"
                sx={{
                  background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(99, 102, 241, 0.1) 100%)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  fontWeight: 600,
                }}
              />
              <Chip 
                label={`${health.total_metrics} Metrics`}
                size="small"
                sx={{
                  background: 'linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(236, 72, 153, 0.1) 100%)',
                  border: '1px solid rgba(236, 72, 153, 0.3)',
                  fontWeight: 600,
                }}
              />
              <Chip 
                label={`${health.total_risk_scores} Risk Scores`}
                size="small"
                sx={{
                  background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(6, 182, 212, 0.1) 100%)',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  fontWeight: 600,
                }}
              />
            </Box>
          )}
        </Box>
      </Container>
    </Box>
  )
}



