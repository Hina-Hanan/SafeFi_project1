import React, { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  Slider,
  FormControlLabel,
  Switch,
  CircularProgress,
  Chip,
  Stack,
} from '@mui/material';
import {
  Email as EmailIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  NotificationsActive as NotificationIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { colors } from '../utils/riskColors';

interface SubscriptionRequest {
  email: string;
  high_risk_threshold: number;
  medium_risk_threshold: number;
  notify_on_high: boolean;
  notify_on_medium: boolean;
}

interface SubscriptionResponse {
  success: boolean;
  message: string;
  email: string;
  subscriber_id?: string;
  is_active?: boolean;
  is_verified?: boolean;
}

interface EmailAlertStatus {
  enabled: boolean;
  total_subscribers: number;
  active_subscribers: number;
}

const subscribeToAlerts = async (data: SubscriptionRequest): Promise<SubscriptionResponse> => {
  const response = await api.post<SubscriptionResponse>('/email-alerts/subscribe', data);
  return response.data;
};

const getEmailAlertStatus = async (): Promise<EmailAlertStatus> => {
  const response = await api.get<EmailAlertStatus>('/email-alerts/status');
  return response.data;
};

export default function EmailSubscription() {
  const [email, setEmail] = useState('');
  const [highRiskThreshold, setHighRiskThreshold] = useState(70);
  const [mediumRiskThreshold, setMediumRiskThreshold] = useState(40);
  const [notifyOnHigh, setNotifyOnHigh] = useState(true);
  const [notifyOnMedium, setNotifyOnMedium] = useState(true);
  const [showSuccess, setShowSuccess] = useState(false);

  const { data: status } = useQuery({
    queryKey: ['email-alert-status'],
    queryFn: getEmailAlertStatus,
    refetchInterval: 30000,
  });

  const subscriptionMutation = useMutation({
    mutationFn: subscribeToAlerts,
    onSuccess: () => {
      setShowSuccess(true);
      setEmail('');
      setTimeout(() => setShowSuccess(false), 5000);
    },
  });

  const handleSubscribe = () => {
    if (!email) return;

    subscriptionMutation.mutate({
      email,
      high_risk_threshold: highRiskThreshold,
      medium_risk_threshold: mediumRiskThreshold,
      notify_on_high: notifyOnHigh,
      notify_on_medium: notifyOnMedium,
    });
  };

  const isValidEmail = (email: string) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
  };

  return (
    <Box>
      {/* Header */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          background: colors.darkGray,
          border: `2px solid ${colors.gray}`,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              background: colors.black,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `2px solid ${colors.gray}`,
            }}
          >
            <EmailIcon sx={{ fontSize: 32, color: colors.white }} />
          </Box>
          <Box>
            <Typography variant="h5" sx={{ color: colors.white, fontWeight: 700 }}>
              Email Risk Alerts
            </Typography>
            <Typography variant="body2" sx={{ color: colors.textGray }}>
              Get notified when protocols exceed your risk thresholds
            </Typography>
          </Box>
        </Box>

        {status && (
          <Stack direction="row" spacing={1}>
            <Chip
              label={status.enabled ? 'ENABLED' : 'DISABLED'}
              size="small"
              sx={{
                background: status.enabled ? colors.greenDark : colors.redDark,
                border: `2px solid ${status.enabled ? colors.green : colors.red}`,
                color: colors.white,
                fontWeight: 600,
              }}
            />
            <Chip
              label={`${status.active_subscribers} Active Subscribers`}
              size="small"
              sx={{
                background: colors.black,
                border: `2px solid ${colors.gray}`,
                color: colors.white,
                fontWeight: 600,
              }}
            />
          </Stack>
        )}
      </Paper>

      {/* Success Message */}
      {showSuccess && (
        <Alert
          severity="success"
          icon={<CheckIcon />}
          sx={{
            mb: 3,
            background: colors.greenDark,
            border: `2px solid ${colors.green}`,
            color: colors.white,
            '& .MuiAlert-icon': {
              color: colors.green,
            },
          }}
        >
          Successfully subscribed! You'll receive alerts when risk thresholds are exceeded.
        </Alert>
      )}

      {/* Error Message */}
      {subscriptionMutation.isError && (
        <Alert
          severity="error"
          icon={<ErrorIcon />}
          sx={{
            mb: 3,
            background: colors.redDark,
            border: `2px solid ${colors.red}`,
            color: colors.white,
            '& .MuiAlert-icon': {
              color: colors.red,
            },
          }}
        >
          {(subscriptionMutation.error as any)?.response?.data?.detail || 'Subscription failed. Please try again.'}
        </Alert>
      )}

      {/* Subscription Form */}
      <Paper
        sx={{
          p: 3,
          background: colors.black,
          border: `2px solid ${colors.gray}`,
        }}
      >
        <Typography variant="h6" sx={{ color: colors.white, fontWeight: 600, mb: 3 }}>
          Subscribe to Alerts
        </Typography>

        {/* Email Input */}
        <TextField
          fullWidth
          label="Email Address"
          variant="outlined"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="your@email.com"
          disabled={subscriptionMutation.isPending}
          error={email.length > 0 && !isValidEmail(email)}
          helperText={email.length > 0 && !isValidEmail(email) ? 'Invalid email format' : ''}
          sx={{
            mb: 3,
            '& .MuiOutlinedInput-root': {
              background: colors.darkGray,
              color: colors.white,
              '& fieldset': {
                borderColor: colors.gray,
                borderWidth: 2,
              },
              '&:hover fieldset': {
                borderColor: colors.white,
              },
              '&.Mui-focused fieldset': {
                borderColor: colors.white,
              },
            },
            '& .MuiInputLabel-root': {
              color: colors.textGray,
              '&.Mui-focused': {
                color: colors.white,
              },
            },
            '& .MuiFormHelperText-root': {
              color: colors.red,
            },
          }}
        />

        {/* High Risk Threshold */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: colors.white, fontWeight: 600, mb: 1 }}>
            High Risk Threshold: {highRiskThreshold}%
          </Typography>
          <Slider
            value={highRiskThreshold}
            onChange={(_, value) => setHighRiskThreshold(value as number)}
            min={50}
            max={100}
            disabled={subscriptionMutation.isPending}
            sx={{
              color: colors.red,
              '& .MuiSlider-thumb': {
                background: colors.red,
                border: `2px solid ${colors.white}`,
              },
              '& .MuiSlider-track': {
                background: colors.red,
              },
              '& .MuiSlider-rail': {
                background: colors.gray,
              },
            }}
          />
          <Typography variant="caption" sx={{ color: colors.textGray }}>
            Alert when protocol risk exceeds this threshold
          </Typography>
        </Box>

        {/* Medium Risk Threshold */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: colors.white, fontWeight: 600, mb: 1 }}>
            Medium Risk Threshold: {mediumRiskThreshold}%
          </Typography>
          <Slider
            value={mediumRiskThreshold}
            onChange={(_, value) => setMediumRiskThreshold(value as number)}
            min={20}
            max={70}
            disabled={subscriptionMutation.isPending}
            sx={{
              color: colors.orange,
              '& .MuiSlider-thumb': {
                background: colors.orange,
                border: `2px solid ${colors.white}`,
              },
              '& .MuiSlider-track': {
                background: colors.orange,
              },
              '& .MuiSlider-rail': {
                background: colors.gray,
              },
            }}
          />
          <Typography variant="caption" sx={{ color: colors.textGray }}>
            Alert when protocol risk exceeds this threshold
          </Typography>
        </Box>

        {/* Notification Preferences */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ color: colors.white, fontWeight: 600, mb: 2 }}>
            Notification Preferences
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={notifyOnHigh}
                onChange={(e) => setNotifyOnHigh(e.target.checked)}
                disabled={subscriptionMutation.isPending}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: colors.red,
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: colors.red,
                  },
                }}
              />
            }
            label="Notify on High Risk"
            sx={{
              color: colors.white,
              display: 'block',
              mb: 1,
            }}
          />
          
          <FormControlLabel
            control={
              <Switch
                checked={notifyOnMedium}
                onChange={(e) => setNotifyOnMedium(e.target.checked)}
                disabled={subscriptionMutation.isPending}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: colors.orange,
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: colors.orange,
                  },
                }}
              />
            }
            label="Notify on Medium Risk"
            sx={{
              color: colors.white,
              display: 'block',
            }}
          />
        </Box>

        {/* Subscribe Button */}
        <Button
          fullWidth
          variant="contained"
          size="large"
          startIcon={subscriptionMutation.isPending ? <CircularProgress size={20} color="inherit" /> : <NotificationIcon />}
          onClick={handleSubscribe}
          disabled={!email || !isValidEmail(email) || subscriptionMutation.isPending || !status?.enabled}
          sx={{
            background: colors.white,
            color: colors.black,
            fontWeight: 700,
            padding: '12px 24px',
            border: `2px solid ${colors.white}`,
            '&:hover': {
              background: colors.gray,
            },
            '&:disabled': {
              background: colors.darkGray,
              color: colors.textGray,
              border: `2px solid ${colors.gray}`,
            },
          }}
        >
          {subscriptionMutation.isPending ? 'Subscribing...' : 'Subscribe to Alerts'}
        </Button>

        {!status?.enabled && (
          <Alert
            severity="warning"
            sx={{
              mt: 2,
              background: colors.orangeDark,
              border: `2px solid ${colors.orange}`,
              color: colors.white,
            }}
          >
            Email alerts are currently disabled. Please configure SMTP settings in the backend.
          </Alert>
        )}
      </Paper>

      {/* How It Works */}
      <Paper
        sx={{
          p: 3,
          mt: 3,
          background: colors.darkGray,
          border: `2px solid ${colors.gray}`,
        }}
      >
        <Typography variant="h6" sx={{ color: colors.white, fontWeight: 600, mb: 2 }}>
          How Email Alerts Work
        </Typography>

        <Stack spacing={2}>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography sx={{ color: colors.green, fontWeight: 700 }}>1.</Typography>
            <Typography sx={{ color: colors.textGray }}>
              Enter your email and set your preferred risk thresholds
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography sx={{ color: colors.green, fontWeight: 700 }}>2.</Typography>
            <Typography sx={{ color: colors.textGray }}>
              Our system monitors all protocols in real-time
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography sx={{ color: colors.green, fontWeight: 700 }}>3.</Typography>
            <Typography sx={{ color: colors.textGray }}>
              You'll receive an email when any protocol exceeds your thresholds
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Typography sx={{ color: colors.green, fontWeight: 700 }}>4.</Typography>
            <Typography sx={{ color: colors.textGray }}>
              Unsubscribe anytime using the link in any email
            </Typography>
          </Box>
        </Stack>
      </Paper>
    </Box>
  );
}


