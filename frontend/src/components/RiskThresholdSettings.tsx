import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Slider,
  Button,
  Alert,
  Switch,
  FormControlLabel,
  Chip,
  Grid,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsOff as NotificationsOffIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
} from '@mui/icons-material';

interface ThresholdSettings {
  enabled: boolean;
  highRiskThreshold: number;
  mediumRiskThreshold: number;
  notifyOnHigh: boolean;
  notifyOnMedium: boolean;
}

interface RiskThresholdSettingsProps {
  onSettingsChange?: (settings: ThresholdSettings) => void;
}

const RiskThresholdSettings: React.FC<RiskThresholdSettingsProps> = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState<ThresholdSettings>(() => {
    // Load from localStorage
    const saved = localStorage.getItem('riskThresholdSettings');
    return saved ? JSON.parse(saved) : {
      enabled: true,
      highRiskThreshold: 70,
      mediumRiskThreshold: 40,
      notifyOnHigh: true,
      notifyOnMedium: true,
    };
  });

  const [showSuccess, setShowSuccess] = useState(false);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('riskThresholdSettings', JSON.stringify(settings));
    onSettingsChange?.(settings);
  }, [settings, onSettingsChange]);

  const handleSave = () => {
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const getRiskColor = (score: number) => {
    if (score >= settings.highRiskThreshold) return '#ef4444';
    if (score >= settings.mediumRiskThreshold) return '#f59e0b';
    return '#10b981';
  };

  const getRiskLabel = (score: number) => {
    if (score >= settings.highRiskThreshold) return 'High Risk';
    if (score >= settings.mediumRiskThreshold) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <Card
      sx={{
        background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      }}
    >
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 3,
                background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
              }}
            >
              <SettingsIcon sx={{ color: 'white', fontSize: '1.5rem' }} />
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
                Risk Alert Settings
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Configure your risk threshold alerts
              </Typography>
            </Box>
          </Box>
          <FormControlLabel
            control={
              <Switch
                checked={settings.enabled}
                onChange={(e) => setSettings({ ...settings, enabled: e.target.checked })}
                color="primary"
              />
            }
            label={settings.enabled ? 'Enabled' : 'Disabled'}
          />
        </Box>

        {showSuccess && (
          <Alert 
            severity="success" 
            sx={{ 
              mb: 2,
              background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
            icon={<CheckCircleIcon />}
          >
            Alert settings saved successfully!
          </Alert>
        )}

        <Box sx={{ opacity: settings.enabled ? 1 : 0.5, pointerEvents: settings.enabled ? 'auto' : 'none' }}>
          {/* High Risk Threshold */}
          <Box mb={4}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="subtitle2" fontWeight="600" gutterBottom>
                  High Risk Threshold
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Alert when risk score exceeds this value
                </Typography>
              </Box>
              <Chip
                label={`${settings.highRiskThreshold}%`}
                sx={{
                  background: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '1rem',
                  px: 1,
                }}
              />
            </Box>
            <Slider
              value={settings.highRiskThreshold}
              onChange={(_, value) => setSettings({ 
                ...settings, 
                highRiskThreshold: value as number,
                mediumRiskThreshold: Math.min(settings.mediumRiskThreshold, (value as number) - 10)
              })}
              min={50}
              max={100}
              step={5}
              marks={[
                { value: 50, label: '50%' },
                { value: 70, label: '70%' },
                { value: 90, label: '90%' },
                { value: 100, label: '100%' },
              ]}
              sx={{
                '& .MuiSlider-thumb': {
                  background: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
                  boxShadow: '0 0 20px rgba(239, 68, 68, 0.6)',
                },
                '& .MuiSlider-track': {
                  background: 'linear-gradient(90deg, #ef4444 0%, #f87171 100%)',
                },
                '& .MuiSlider-rail': {
                  opacity: 0.3,
                },
              }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifyOnHigh}
                  onChange={(e) => setSettings({ ...settings, notifyOnHigh: e.target.checked })}
                  color="error"
                />
              }
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  {settings.notifyOnHigh ? <NotificationsIcon fontSize="small" /> : <NotificationsOffIcon fontSize="small" />}
                  <Typography variant="body2">
                    {settings.notifyOnHigh ? 'Alerts enabled' : 'Alerts disabled'}
                  </Typography>
                </Box>
              }
            />
          </Box>

          <Divider sx={{ my: 3, borderColor: 'rgba(99, 102, 241, 0.2)' }} />

          {/* Medium Risk Threshold */}
          <Box mb={4}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="subtitle2" fontWeight="600" gutterBottom>
                  Medium Risk Threshold
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Alert when risk score exceeds this value
                </Typography>
              </Box>
              <Chip
                label={`${settings.mediumRiskThreshold}%`}
                sx={{
                  background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '1rem',
                  px: 1,
                }}
              />
            </Box>
            <Slider
              value={settings.mediumRiskThreshold}
              onChange={(_, value) => setSettings({ 
                ...settings, 
                mediumRiskThreshold: Math.min(value as number, settings.highRiskThreshold - 10)
              })}
              min={20}
              max={settings.highRiskThreshold - 10}
              step={5}
              marks={[
                { value: 20, label: '20%' },
                { value: 40, label: '40%' },
                { value: 60, label: '60%' },
              ]}
              sx={{
                '& .MuiSlider-thumb': {
                  background: 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)',
                  boxShadow: '0 0 20px rgba(245, 158, 11, 0.6)',
                },
                '& .MuiSlider-track': {
                  background: 'linear-gradient(90deg, #f59e0b 0%, #fbbf24 100%)',
                },
                '& .MuiSlider-rail': {
                  opacity: 0.3,
                },
              }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifyOnMedium}
                  onChange={(e) => setSettings({ ...settings, notifyOnMedium: e.target.checked })}
                  color="warning"
                />
              }
              label={
                <Box display="flex" alignItems="center" gap={1}>
                  {settings.notifyOnMedium ? <NotificationsIcon fontSize="small" /> : <NotificationsOffIcon fontSize="small" />}
                  <Typography variant="body2">
                    {settings.notifyOnMedium ? 'Alerts enabled' : 'Alerts disabled'}
                  </Typography>
                </Box>
              }
            />
          </Box>

          {/* Preview */}
          <Box
            sx={{
              p: 3,
              borderRadius: 3,
              background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(236, 72, 153, 0.1) 100%)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
            }}
          >
            <Typography variant="subtitle2" fontWeight="600" gutterBottom>
              Alert Preview
            </Typography>
            <Grid container spacing={2} mt={1}>
              {[25, 45, 75, 95].map((score) => (
                <Grid item xs={6} sm={3} key={score}>
                  <Box
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      background: `${getRiskColor(score)}20`,
                      border: `2px solid ${getRiskColor(score)}`,
                      textAlign: 'center',
                    }}
                  >
                    <Typography variant="h6" fontWeight="bold" sx={{ color: getRiskColor(score) }}>
                      {score}%
                    </Typography>
                    <Typography variant="caption" sx={{ color: getRiskColor(score) }}>
                      {getRiskLabel(score)}
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Save Button */}
          <Box mt={3} display="flex" justifyContent="flex-end">
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              sx={{
                background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
                boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
                px: 4,
                py: 1.5,
                fontWeight: 600,
                '&:hover': {
                  boxShadow: '0 6px 30px rgba(99, 102, 241, 0.6)',
                  transform: 'translateY(-2px)',
                },
              }}
            >
              Save Settings
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default RiskThresholdSettings;
















