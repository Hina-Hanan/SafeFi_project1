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
} from '@mui/material'
import { PlayArrow, Refresh, TrendingUp, Speed } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { fetchModelPerformance, trainModels, compareModelVersions } from '../services/api'

export default function ModelMetrics() {
  const [selectedModel, setSelectedModel] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: modelPerformance, isLoading, error } = useQuery({
    queryKey: ['model-performance'],
    queryFn: fetchModelPerformance,
    refetchInterval: 60000,
  })

  const trainMutation = useMutation({
    mutationFn: trainModels,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['model-performance'] })
    },
  })

  const { data: modelVersions } = useQuery({
    queryKey: ['model-versions', selectedModel],
    queryFn: () => compareModelVersions(selectedModel),
    enabled: !!selectedModel,
  })

  const handleTrainModels = () => {
    trainMutation.mutate()
  }

  const getPerformanceColor = (score: number): 'success' | 'warning' | 'error' => {
    if (score >= 0.8) return 'success'
    if (score >= 0.6) return 'warning'
    return 'error'
  }

  const getPerformanceLabel = (score: number): string => {
    if (score >= 0.8) return 'Excellent'
    if (score >= 0.6) return 'Good'
    if (score >= 0.4) return 'Fair'
    return 'Poor'
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">ML Model Performance</Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="contained"
              startIcon={trainMutation.isPending ? <CircularProgress size={16} /> : <PlayArrow />}
              onClick={handleTrainModels}
              disabled={trainMutation.isPending}
              size="small"
            >
              {trainMutation.isPending ? 'Training...' : 'Train Models'}
            </Button>
            <IconButton onClick={() => queryClient.invalidateQueries({ queryKey: ['model-performance'] })}>
              <Refresh />
            </IconButton>
          </Box>
        </Box>

        {trainMutation.isError && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Failed to train models: {trainMutation.error?.message}
          </Alert>
        )}

        {trainMutation.isSuccess && (
          <Alert severity="success" sx={{ mb: 2 }}>
            Models trained successfully!
          </Alert>
        )}

        {isLoading ? (
          <Box display="flex" justifyContent="center" py={4}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error">
            Failed to load model performance data
          </Alert>
        ) : modelPerformance ? (
          <Box>
            {/* Overall Performance Summary */}
            <Grid container spacing={2} mb={3}>
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="primary">
                    {(modelPerformance.f1 * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    F1 Score
                  </Typography>
                  <Chip
                    label={getPerformanceLabel(modelPerformance.f1)}
                    color={getPerformanceColor(modelPerformance.f1)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="success.main">
                    {(modelPerformance.accuracy * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Accuracy
                  </Typography>
                  <Chip
                    label={getPerformanceLabel(modelPerformance.accuracy)}
                    color={getPerformanceColor(modelPerformance.accuracy)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>

              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="warning.main">
                    {(modelPerformance.precision * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Precision
                  </Typography>
                  <Chip
                    label={getPerformanceLabel(modelPerformance.precision)}
                    color={getPerformanceColor(modelPerformance.precision)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>

              <Grid item xs={12} sm={3}>
                <Box textAlign="center" p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="h4" color="info.main">
                    {(modelPerformance.recall * 100).toFixed(1)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Recall
                  </Typography>
                  <Chip
                    label={getPerformanceLabel(modelPerformance.recall)}
                    color={getPerformanceColor(modelPerformance.recall)}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                </Box>
              </Grid>
            </Grid>

            {/* Model Details */}
            <Box mb={3}>
              <Typography variant="subtitle1" gutterBottom>
                Model Details
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Model Name
                    </Typography>
                    <Typography variant="h6">
                      {modelPerformance.model_name}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box p={2} sx={{ backgroundColor: 'grey.50', borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Model Version
                    </Typography>
                    <Typography variant="h6">
                      {modelPerformance.model_version || 'N/A'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </Box>

            {/* Performance Metrics Visualization */}
            <Box mb={3}>
              <Typography variant="subtitle1" gutterBottom>
                Performance Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">F1 Score</Typography>
                      <Typography variant="body2">{(modelPerformance.f1 * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={modelPerformance.f1 * 100}
                      color={getPerformanceColor(modelPerformance.f1)}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Accuracy</Typography>
                      <Typography variant="body2">{(modelPerformance.accuracy * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={modelPerformance.accuracy * 100}
                      color={getPerformanceColor(modelPerformance.accuracy)}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Precision</Typography>
                      <Typography variant="body2">{(modelPerformance.precision * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={modelPerformance.precision * 100}
                      color={getPerformanceColor(modelPerformance.precision)}
                    />
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Typography variant="body2">Recall</Typography>
                      <Typography variant="body2">{(modelPerformance.recall * 100).toFixed(1)}%</Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={modelPerformance.recall * 100}
                      color={getPerformanceColor(modelPerformance.recall)}
                    />
                  </Box>
                </Grid>
              </Grid>
            </Box>

            {/* Model Status */}
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Model Status
              </Typography>
              <Box display="flex" gap={2} alignItems="center">
                <Chip
                  icon={<Speed />}
                  label="Production Ready"
                  color="success"
                  variant="outlined"
                />
                <Chip
                  icon={<TrendingUp />}
                  label="Active Monitoring"
                  color="info"
                  variant="outlined"
                />
                <Typography variant="body2" color="text.secondary">
                  Last updated: {new Date().toLocaleString()}
                </Typography>
              </Box>
            </Box>
          </Box>
        ) : (
          <Box textAlign="center" py={4}>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              No trained models available
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Click "Train Models" to start training ML models for risk assessment
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  )
}