import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
} from '@mui/material'
import { Refresh, TrendingUp, TrendingDown } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { fetchProtocolRiskHistory, fetchProtocolRiskDetails } from '../services/api'
import { RiskLevel } from '../types'

interface RiskChartProps {
  protocolId: string
  protocolName?: string
}

const getRiskColor = (riskLevel: RiskLevel): string => {
  switch (riskLevel) {
    case 'low': return '#4caf50'
    case 'medium': return '#ff9800'
    case 'high': return '#f44336'
    default: return '#9e9e9e'
  }
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (dateString: string): string => {
  return new Date(dateString).toLocaleTimeString()
}

export default function RiskChart({ protocolId, protocolName }: RiskChartProps) {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d')
  
  const { data: riskHistory, isLoading: historyLoading, error: historyError } = useQuery({
    queryKey: ['risk-history', protocolId, timeRange],
    queryFn: () => fetchProtocolRiskHistory(protocolId, parseInt(timeRange.replace('d', ''))),
    enabled: !!protocolId,
    refetchInterval: 30000,
  })

  const { data: riskDetails, isLoading: detailsLoading } = useQuery({
    queryKey: ['risk-details', protocolId],
    queryFn: () => fetchProtocolRiskDetails(protocolId),
    enabled: !!protocolId,
    refetchInterval: 30000,
  })

  if (historyLoading || detailsLoading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    )
  }

  if (historyError) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            Failed to load risk data for {protocolName || protocolId}
          </Alert>
        </CardContent>
      </Card>
    )
  }

  const currentRisk = riskDetails || riskHistory?.[0]
  const riskTrend = riskHistory && riskHistory.length > 1 ? 
    riskHistory[0].risk_score - riskHistory[riskHistory.length - 1].risk_score : 0

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">
            Risk Analysis: {protocolName || protocolId}
          </Typography>
          <Box display="flex" gap={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 100 }}>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={timeRange}
                label="Time Range"
                onChange={(e) => setTimeRange(e.target.value as any)}
              >
                <MenuItem value="7d">7 Days</MenuItem>
                <MenuItem value="30d">30 Days</MenuItem>
                <MenuItem value="90d">90 Days</MenuItem>
              </Select>
            </FormControl>
            <IconButton size="small">
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {currentRisk && (
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="h4" color={getRiskColor(currentRisk.risk_level)}>
                  {(currentRisk.risk_score * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Current Risk Score
                </Typography>
                <Chip
                  label={currentRisk.risk_level.toUpperCase()}
                  color={currentRisk.risk_level === 'high' ? 'error' : 
                         currentRisk.risk_level === 'medium' ? 'warning' : 'success'}
                  size="small"
                  sx={{ mt: 1 }}
                />
              </Box>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                  {riskTrend > 0 ? <TrendingUp color="error" /> : 
                   riskTrend < 0 ? <TrendingDown color="success" /> : null}
                  <Typography variant="h6" ml={1}>
                    {riskTrend > 0 ? '+' : ''}{(riskTrend * 100).toFixed(1)}%
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Risk Trend ({timeRange})
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={12} sm={4}>
              <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="h6">
                  {riskHistory?.length || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Data Points
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Last: {riskHistory?.[0] ? formatTime(riskHistory[0].timestamp) : 'N/A'}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        )}

        {/* Risk Score Timeline */}
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Risk Score Timeline
          </Typography>
          <Box sx={{ height: 200, backgroundColor: 'grey.50', borderRadius: 1, p: 2 }}>
            {riskHistory && riskHistory.length > 0 ? (
              <Box display="flex" alignItems="end" height="100%" gap={1}>
                {riskHistory.slice(0, 20).map((point: any, index: number) => (
                  <Box
                    key={index}
                    sx={{
                      flex: 1,
                      height: `${point.risk_score * 100}%`,
                      backgroundColor: getRiskColor(point.risk_level),
                      borderRadius: '4px 4px 0 0',
                      minHeight: 4,
                      position: 'relative',
                    }}
                    title={`${formatDate(point.timestamp)}: ${(point.risk_score * 100).toFixed(1)}%`}
                  />
                ))}
              </Box>
            ) : (
              <Box display="flex" alignItems="center" justifyContent="center" height="100%">
                <Typography color="text.secondary">No historical data available</Typography>
              </Box>
            )}
          </Box>
        </Box>

        {/* Risk Breakdown */}
        {riskDetails && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Risk Breakdown
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Box p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Volatility Score
                  </Typography>
                  <Typography variant="h6">
                    {riskDetails.volatility_score ? 
                      (riskDetails.volatility_score * 100).toFixed(1) + '%' : 
                      'N/A'}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Box p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Liquidity Score
                  </Typography>
                  <Typography variant="h6">
                    {riskDetails.liquidity_score ? 
                      (riskDetails.liquidity_score * 100).toFixed(1) + '%' : 
                      'N/A'}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}