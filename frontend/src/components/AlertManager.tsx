import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Button,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Switch,
  FormControlLabel,
  Divider,
  Paper,
} from '@mui/material'
import {
  Warning,
  Error,
  Info,
  CheckCircle,
  Notifications,
  NotificationsOff,
  Settings,
  Refresh,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { fetchProtocols } from '../services/api'

interface AlertRule {
  id: string
  name: string
  condition: string
  threshold: number
  enabled: boolean
  severity: 'low' | 'medium' | 'high'
}

interface Alert {
  id: string
  protocolId: string
  protocolName: string
  message: string
  severity: 'low' | 'medium' | 'high'
  timestamp: string
  acknowledged: boolean
}

export default function AlertManager() {
  const [alertRules, setAlertRules] = useState<AlertRule[]>([
    {
      id: '1',
      name: 'High Risk Threshold',
      condition: 'risk_score > 0.8',
      threshold: 0.8,
      enabled: true,
      severity: 'high',
    },
    {
      id: '2',
      name: 'Price Volatility',
      condition: 'price_change_24h > 20%',
      threshold: 20,
      enabled: true,
      severity: 'medium',
    },
    {
      id: '3',
      name: 'Low Liquidity',
      condition: 'volume_24h < 1M',
      threshold: 1000000,
      enabled: false,
      severity: 'low',
    },
  ])

  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: '1',
      protocolId: 'uniswap',
      protocolName: 'Uniswap',
      message: 'Risk score exceeded 80% threshold',
      severity: 'high',
      timestamp: new Date().toISOString(),
      acknowledged: false,
    },
    {
      id: '2',
      protocolId: 'aave',
      protocolName: 'Aave',
      message: 'Price volatility detected (>20% change)',
      severity: 'medium',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      acknowledged: true,
    },
  ])

  const { data: protocols } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  })

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high': return <Error color="error" />
      case 'medium': return <Warning color="warning" />
      case 'low': return <Info color="info" />
      default: return <CheckCircle color="success" />
    }
  }

  const getSeverityColor = (severity: string): 'error' | 'warning' | 'info' | 'success' => {
    switch (severity) {
      case 'high': return 'error'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'success'
    }
  }

  const toggleRule = (ruleId: string) => {
    setAlertRules(prev => prev.map(rule => 
      rule.id === ruleId ? { ...rule, enabled: !rule.enabled } : rule
    ))
  }

  const acknowledgeAlert = (alertId: string) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, acknowledged: true } : alert
    ))
  }

  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged)
  const acknowledgedAlerts = alerts.filter(alert => alert.acknowledged)

  return (
    <Grid container spacing={3}>
      {/* Alert Rules */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Alert Rules</Typography>
              <Box>
                <IconButton size="small">
                  <Settings />
                </IconButton>
                <IconButton size="small">
                  <Refresh />
                </IconButton>
              </Box>
            </Box>
            
            <List>
              {alertRules.map((rule) => (
                <ListItem key={rule.id} divider>
                  <ListItemIcon>
                    {getSeverityIcon(rule.severity)}
                  </ListItemIcon>
                  <ListItemText
                    primary={rule.name}
                    secondary={`${rule.condition} (threshold: ${rule.threshold})`}
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={rule.enabled}
                        onChange={() => toggleRule(rule.id)}
                        size="small"
                      />
                    }
                    label=""
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Active Alerts */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">Active Alerts</Typography>
              <Chip
                label={`${unacknowledgedAlerts.length} unread`}
                color="error"
                size="small"
              />
            </Box>

            {unacknowledgedAlerts.length === 0 ? (
              <Alert severity="success">
                No active alerts
              </Alert>
            ) : (
              <List>
                {unacknowledgedAlerts.map((alert) => (
                  <ListItem key={alert.id} divider>
                    <ListItemIcon>
                      {getSeverityIcon(alert.severity)}
                    </ListItemIcon>
                    <ListItemText
                      primary={alert.message}
                      secondary={`${alert.protocolName} • ${new Date(alert.timestamp).toLocaleString()}`}
                    />
                    <Button
                      size="small"
                      onClick={() => acknowledgeAlert(alert.id)}
                    >
                      Acknowledge
                    </Button>
                  </ListItem>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Alert History */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Alert History
            </Typography>
            
            {acknowledgedAlerts.length === 0 ? (
              <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                No acknowledged alerts
              </Typography>
            ) : (
              <List>
                {acknowledgedAlerts.map((alert, index) => (
                  <React.Fragment key={alert.id}>
                    <ListItem>
                      <ListItemIcon>
                        {getSeverityIcon(alert.severity)}
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.message}
                        secondary={`${alert.protocolName} • ${new Date(alert.timestamp).toLocaleString()}`}
                      />
                      <Chip
                        label="Acknowledged"
                        color="success"
                        size="small"
                      />
                    </ListItem>
                    {index < acknowledgedAlerts.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Alert Statistics */}
      <Grid item xs={12}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Alert Statistics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="error.main">
                  {alerts.filter(a => a.severity === 'high').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  High Severity
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="warning.main">
                  {alerts.filter(a => a.severity === 'medium').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Medium Severity
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="info.main">
                  {alerts.filter(a => a.severity === 'low').length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Low Severity
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main">
                  {alertRules.filter(r => r.enabled).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Rules
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Grid>
    </Grid>
  )
}