import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Button,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import { Refresh, TrendingUp, TrendingDown, Security, AttachMoney } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { fetchProtocols, calculateBatchRisk } from '../services/api'
import { RiskLevel } from '../types'

export default function PortfolioAnalyzer() {
  const [selectedProtocols, setSelectedProtocols] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'risk' | 'tvl' | 'volume'>('risk')

  const { data: protocols, isLoading, error, refetch } = useQuery({
    queryKey: ['protocols'],
    queryFn: fetchProtocols,
    refetchInterval: 30000,
  })

  const calculatePortfolioRisk = () => {
    if (!protocols || selectedProtocols.length === 0) return null

    const selectedProtocolData = protocols.filter((p: any) => 
      selectedProtocols.includes(p.protocol?.id || p.id)
    )

    const totalTVL = selectedProtocolData.reduce((sum: number, p: any) => 
      sum + (p.latest_metrics?.tvl_usd || 0), 0
    )

    const weightedRiskScore = selectedProtocolData.reduce((sum: number, p: any) => {
      const tvl = p.latest_metrics?.tvl_usd || 0
      const riskScore = p.latest_risk?.risk_score || 0.5
      return sum + (riskScore * tvl)
    }, 0) / totalTVL

    const riskDistribution = selectedProtocolData.reduce((acc: any, p: any) => {
      const riskLevel = p.latest_risk?.risk_level || 'medium'
      acc[riskLevel] = (acc[riskLevel] || 0) + 1
      return acc
    }, {})

    return {
      totalTVL,
      weightedRiskScore,
      riskDistribution,
      protocolCount: selectedProtocolData.length,
    }
  }

  const portfolioRisk = calculatePortfolioRisk()

  const getRiskColor = (riskLevel: RiskLevel): string => {
    switch (riskLevel) {
      case 'low': return '#4caf50'
      case 'medium': return '#ff9800'
      case 'high': return '#f44336'
      default: return '#9e9e9e'
    }
  }

  const formatNumber = (num: number): string => {
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`
    if (num >= 1e3) return `$${(num / 1e3).toFixed(1)}K`
    return `$${num.toFixed(2)}`
  }

  const getOverallRiskLevel = (score: number): RiskLevel => {
    if (score >= 0.7) return 'high'
    if (score >= 0.4) return 'medium'
    return 'low'
  }

  if (isLoading) {
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

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            <IconButton onClick={() => refetch()} size="small">
              <Refresh />
            </IconButton>
          }>
            Failed to load portfolio data
          </Alert>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Portfolio Risk Analyzer</Typography>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Sort by</InputLabel>
              <Select
                value={sortBy}
                label="Sort by"
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <MenuItem value="risk">Risk Score</MenuItem>
                <MenuItem value="tvl">TVL</MenuItem>
                <MenuItem value="volume">Volume</MenuItem>
              </Select>
            </FormControl>
            <IconButton onClick={() => refetch()} size="small">
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {/* Portfolio Summary */}
        {portfolioRisk && (
          <Box mb={3}>
            <Typography variant="subtitle1" gutterBottom>
              Portfolio Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color={getRiskColor(getOverallRiskLevel(portfolioRisk.weightedRiskScore))}>
                    {(portfolioRisk.weightedRiskScore * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Weighted Risk Score
                  </Typography>
                  <Chip
                    label={getOverallRiskLevel(portfolioRisk.weightedRiskScore).toUpperCase()}
                    color={getOverallRiskLevel(portfolioRisk.weightedRiskScore) === 'high' ? 'error' : 
                           getOverallRiskLevel(portfolioRisk.weightedRiskScore) === 'medium' ? 'warning' : 'success'}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="primary">
                    {formatNumber(portfolioRisk.totalTVL)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total TVL
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="info.main">
                    {portfolioRisk.protocolCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Protocols
                  </Typography>
                </Box>
              </Grid>

              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h6" color="success.main">
                    {portfolioRisk.riskDistribution.low || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Low Risk
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {portfolioRisk.riskDistribution.medium || 0} Medium | {portfolioRisk.riskDistribution.high || 0} High
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}

        {/* Protocol Selection */}
        <Box mb={3}>
          <Typography variant="subtitle1" gutterBottom>
            Select Protocols for Analysis
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
            {protocols?.slice(0, 10).map((protocol: any) => {
              const protocolId = protocol.protocol?.id || protocol.id
              const protocolName = protocol.protocol?.name || protocol.name
              const isSelected = selectedProtocols.includes(protocolId)
              
              return (
                <Chip
                  key={protocolId}
                  label={protocolName}
                  onClick={() => {
                    if (isSelected) {
                      setSelectedProtocols(prev => prev.filter(id => id !== protocolId))
                    } else {
                      setSelectedProtocols(prev => [...prev, protocolId])
                    }
                  }}
                  color={isSelected ? 'primary' : 'default'}
                  variant={isSelected ? 'filled' : 'outlined'}
                />
              )
            })}
          </Box>
          <Typography variant="caption" color="text.secondary">
            {selectedProtocols.length} protocols selected
          </Typography>
        </Box>

        {/* Protocol Table */}
        <Box>
          <Typography variant="subtitle1" gutterBottom>
            Protocol Details
          </Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Protocol</TableCell>
                  <TableCell align="right">Risk Score</TableCell>
                  <TableCell align="right">TVL</TableCell>
                  <TableCell align="right">24h Volume</TableCell>
                  <TableCell align="right">Price Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {protocols?.slice(0, 20).map((protocol: any) => {
                  const protocolId = protocol.protocol?.id || protocol.id
                  const protocolName = protocol.protocol?.name || protocol.name
                  const riskScore = protocol.latest_risk?.risk_score || 0.5
                  const riskLevel = protocol.latest_risk?.risk_level || 'medium'
                  const tvl = protocol.latest_metrics?.tvl_usd || 0
                  const volume = protocol.latest_metrics?.volume_24h_usd || 0
                  const priceChange = protocol.latest_metrics?.price_change_24h || 0
                  
                  return (
                    <TableRow key={protocolId}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="body2">{protocolName}</Typography>
                          <Chip
                            label={riskLevel.toUpperCase()}
                            size="small"
                            color={riskLevel === 'high' ? 'error' : 
                                   riskLevel === 'medium' ? 'warning' : 'success'}
                          />
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color={getRiskColor(riskLevel)}>
                          {(riskScore * 100).toFixed(1)}%
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {formatNumber(tvl)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {formatNumber(volume)}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={0.5}>
                          {priceChange > 0 ? <TrendingUp color="success" /> : 
                           priceChange < 0 ? <TrendingDown color="error" /> : null}
                          <Typography variant="body2" color={priceChange > 0 ? 'success.main' : 
                                                             priceChange < 0 ? 'error.main' : 'text.secondary'}>
                            {priceChange.toFixed(2)}%
                          </Typography>
                        </Box>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      </CardContent>
    </Card>
  )
}