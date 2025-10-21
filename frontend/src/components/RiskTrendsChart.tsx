import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShowChart as ShowChartIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Legend, Area, AreaChart } from 'recharts';
import { api } from '../services/api';
import { fetchRiskHistoryResilient } from '../services/api';

interface RiskTrendsChartProps {
  protocolId: string;
  protocolName: string;
  days?: number;
}

const RiskTrendsChart: React.FC<RiskTrendsChartProps> = ({ 
  protocolId, 
  protocolName,
  days = 7 
}) => {
  const { data: historyData, isLoading, error, refetch } = useQuery({
    queryKey: ['riskHistory', protocolId, days],
    queryFn: async () => {
      try {
        const arr = await api.getRiskHistory(protocolId, days)
        if (arr && arr.length) return arr
      } catch (_) {}
      // fallback to resilient helper with a neutral base
      return await fetchRiskHistoryResilient(protocolId, days)
    },
    refetchInterval: 60000,
  });

  if (isLoading) {
    return (
      <Card sx={{ 
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
      }}>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" py={8}>
            <CircularProgress sx={{ color: '#6366f1' }} />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ 
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
      }}>
        <CardContent>
          <Alert 
            severity="error"
            sx={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
            }}
          >
            Failed to load risk trends for {protocolName}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!historyData || historyData.length === 0) {
    return (
      <Card sx={{ 
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
      }}>
        <CardContent>
          <Alert 
            severity="info"
            sx={{
              background: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
            }}
          >
            No historical data available for {protocolName}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  // Prepare data for chart
  const allData = historyData.map((item: any) => {
    const timestamp = new Date(item.timestamp);
    return {
      date: timestamp.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      fullDate: timestamp.toISOString().split('T')[0], // For grouping by day
      time: timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      timestamp: timestamp.getTime(),
      riskScore: (item.risk_score * 100).toFixed(1),
      riskScoreNum: item.risk_score * 100,
      riskLevel: item.risk_level,
    };
  }).reverse(); // Reverse to show oldest first

  // Group by date and take average risk score per day for cleaner chart
  const dataByDate = allData.reduce((acc: any, item: any) => {
    const dateKey = item.fullDate;
    if (!acc[dateKey]) {
      acc[dateKey] = {
        date: item.date,
        fullDate: item.fullDate,
        timestamp: item.timestamp,
        riskScores: [],
      };
    }
    acc[dateKey].riskScores.push(item.riskScoreNum);
    return acc;
  }, {});

  // Calculate average for each day
  const chartData = Object.values(dataByDate).map((day: any) => {
    const avgRiskScore = day.riskScores.reduce((sum: number, score: number) => sum + score, 0) / day.riskScores.length;
    return {
      date: day.date,
      fullDate: day.fullDate,
      timestamp: day.timestamp,
      riskScore: avgRiskScore.toFixed(1),
      riskScoreNum: avgRiskScore,
      dataPoints: day.riskScores.length,
    };
  }).sort((a: any, b: any) => a.timestamp - b.timestamp); // Sort by timestamp

  // Calculate trend
  const currentScore = chartData[chartData.length - 1]?.riskScoreNum || 0;
  const previousScore = chartData[0]?.riskScoreNum || 0;
  const trend = currentScore - previousScore;
  const trendPercentage = previousScore > 0 ? ((trend / previousScore) * 100).toFixed(1) : '0';

  const getRiskColor = (score: number) => {
    if (score >= 70) return '#ef4444';
    if (score >= 40) return '#f59e0b';
    return '#10b981';
  };

  const getRiskLabel = (score: number) => {
    if (score >= 70) return 'High Risk';
    if (score >= 40) return 'Medium Risk';
    return 'Low Risk';
  };

  const currentRiskColor = getRiskColor(currentScore);
  const currentRiskLabel = getRiskLabel(currentScore);

  return (
    <Card
      sx={{
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      }}
    >
      <CardContent>
        {/* Header */}
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 3,
                background: `linear-gradient(135deg, ${currentRiskColor} 0%, ${currentRiskColor}cc 100%)`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 4px 20px ${currentRiskColor}60`,
              }}
            >
              <ShowChartIcon sx={{ color: 'white', fontSize: '1.5rem' }} />
            </Box>
            <Box>
              <Typography 
                variant="h6" 
                fontWeight="bold"
                sx={{
                  background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                {protocolName} - Risk Trends
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Last {days} days
              </Typography>
            </Box>
          </Box>
          <Tooltip title="Refresh">
            <IconButton 
              onClick={() => refetch()}
              sx={{
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                '&:hover': {
                  background: 'rgba(99, 102, 241, 0.2)',
                  boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)',
                },
              }}
            >
              <RefreshIcon sx={{ color: '#6366f1' }} />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Current Stats */}
        <Grid container spacing={2} mb={3}>
          <Grid item xs={12} sm={4}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                background: `${currentRiskColor}15`,
                border: `2px solid ${currentRiskColor}`,
              }}
            >
              <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                Current Risk Score
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: currentRiskColor }}>
                {currentScore.toFixed(0)}%
              </Typography>
              <Chip
                label={currentRiskLabel}
                size="small"
                sx={{
                  mt: 1,
                  background: currentRiskColor,
                  color: 'white',
                  fontWeight: 'bold',
                }}
              />
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                background: trend >= 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)',
                border: `2px solid ${trend >= 0 ? '#ef4444' : '#10b981'}`,
              }}
            >
              <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                {days}-Day Change
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                {trend >= 0 ? (
                  <TrendingUpIcon sx={{ color: '#ef4444', fontSize: '2rem' }} />
                ) : (
                  <TrendingDownIcon sx={{ color: '#10b981', fontSize: '2rem' }} />
                )}
                <Typography variant="h4" fontWeight="bold" sx={{ color: trend >= 0 ? '#ef4444' : '#10b981' }}>
                  {trend >= 0 ? '+' : ''}{trend.toFixed(1)}%
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ color: trend >= 0 ? '#ef4444' : '#10b981', mt: 1, display: 'block' }}>
                {trend >= 0 ? 'Increasing' : 'Decreasing'} ({trendPercentage}%)
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                background: 'rgba(99, 102, 241, 0.1)',
                border: '2px solid rgba(99, 102, 241, 0.5)',
              }}
            >
              <Typography variant="caption" color="text.secondary" gutterBottom display="block">
                Data Points
              </Typography>
              <Typography variant="h4" fontWeight="bold" sx={{ color: '#6366f1' }}>
                {chartData.length}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Historical records
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Chart */}
        <Box
          sx={{
            p: 2,
            borderRadius: 3,
            background: 'rgba(0, 0, 0, 0.6)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
          }}
        >
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#ec4899" stopOpacity={0.2}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(99, 102, 241, 0.1)" />
              <XAxis 
                dataKey="date" 
                stroke="#94a3b8"
                style={{ fontSize: '0.75rem' }}
              />
              <YAxis 
                stroke="#94a3b8"
                style={{ fontSize: '0.75rem' }}
                domain={[0, 100]}
                tickFormatter={(value) => `${value}%`}
              />
              <RechartsTooltip
                contentStyle={{
                  background: 'rgba(0, 0, 0, 0.95)',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  borderRadius: '12px',
                  padding: '12px',
                  backdropFilter: 'blur(10px)',
                }}
                labelStyle={{ color: '#e2e8f0', fontWeight: 'bold' }}
                itemStyle={{ color: '#6366f1' }}
                formatter={(value: any) => [`${Number(value).toFixed(1)}%`, 'Risk Score']}
                labelFormatter={(label: any) => `Date: ${label}`}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Area
                type="monotone"
                dataKey="riskScoreNum"
                stroke="#6366f1"
                strokeWidth={3}
                fill="url(#riskGradient)"
                name="Risk Score"
                dot={{ fill: '#6366f1', r: 4 }}
                activeDot={{ r: 6, fill: '#ec4899' }}
              />
              {/* Reference lines for thresholds */}
              <Line
                type="monotone"
                dataKey={() => 70}
                stroke="#ef4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="High Risk (70%)"
              />
              <Line
                type="monotone"
                dataKey={() => 40}
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Medium Risk (40%)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Box>

        {/* Summary */}
        <Box
          mt={3}
          p={2}
          sx={{
            borderRadius: 2,
            background: 'rgba(0, 0, 0, 0.4)',
            border: '1px solid rgba(99, 102, 241, 0.2)',
          }}
        >
          <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
            Analysis Summary
          </Typography>
          <Typography variant="body2" color="text.primary">
            {currentRiskLabel} detected for {protocolName}. 
            Risk score has {trend >= 0 ? 'increased' : 'decreased'} by {Math.abs(trend).toFixed(1)}% 
            over the last {days} days. {currentScore >= 70 ? '⚠️ High risk alert!' : currentScore >= 40 ? '⚡ Moderate risk level' : '✅ Low risk level'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RiskTrendsChart;



