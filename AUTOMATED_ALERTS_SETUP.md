# Automated Data Updates and Email Alerts - Complete Setup Guide

## Overview

Your DeFi Risk Assessment platform now has a fully automated system that:

✅ **Updates data every 15-30 minutes** with small realistic changes
✅ **Recalculates risk scores** automatically based on new data
✅ **Monitors each subscriber's personalized thresholds**
✅ **Sends email alerts** when protocols exceed individual subscriber settings
✅ **Prevents spam** with intelligent cooldown periods
✅ **Runs automatically** on application startup

## What's Been Implemented

### 1. Subscriber-Specific Alert Service
**File:** `backend/app/services/subscriber_alert_service.py`

- Monitors all active email subscribers
- Checks each subscriber's individual thresholds
- Sends personalized alerts based on preferences
- Implements 1-hour cooldown to prevent spam
- Supports both single and batch alerts

### 2. Automated Scheduler
**File:** `backend/app/services/automated_scheduler.py`

- Runs updates every 15-30 minutes (randomized)
- Updates protocol metrics with realistic small changes (±1-3%)
- Recalculates risk scores based on new data
- Checks all subscriber thresholds
- Sends alerts automatically
- Graceful error handling and logging

### 3. Monitoring API
**File:** `backend/app/api/v1/monitoring.py`

New endpoints for monitoring and control:
- `GET /monitoring/scheduler/status` - Check scheduler status
- `POST /monitoring/scheduler/force-update` - Force immediate update
- `POST /monitoring/scheduler/start` - Start scheduler
- `POST /monitoring/scheduler/stop` - Stop scheduler
- `GET /monitoring/alerts/statistics` - Get alert statistics
- `GET /monitoring/alerts/subscriber/{email}/status` - Check subscriber status
- `POST /monitoring/alerts/test/{email}` - Send test alert

### 4. Enhanced Email Subscribers
**Database:** `EmailSubscriber` model already has all needed fields:

```python
- high_risk_threshold: float (default: 70.0)
- medium_risk_threshold: float (default: 40.0)
- notify_on_high: bool (default: True)
- notify_on_medium: bool (default: True)
- last_alert_sent: datetime (tracks last alert time)
```

## How It Works

### Data Update Cycle (Every 15-30 Minutes)

```
1. Update Protocol Metrics
   ↓
   - Apply small realistic changes to TVL, Volume, Price
   - Create new ProtocolMetric entries
   
2. Recalculate Risk Scores
   ↓
   - Apply variations based on market changes
   - Update risk levels (low/medium/high)
   - Create new RiskScore entries
   
3. Check Subscriber Thresholds
   ↓
   - Get all active subscribers
   - Compare each protocol's risk score to each subscriber's thresholds
   - Send personalized alerts if thresholds exceeded
   - Respect 1-hour cooldown period
```

### Alert Logic Per Subscriber

```python
for each subscriber:
    for each protocol:
        risk_score_pct = protocol.risk_score * 100
        
        if risk_score_pct >= subscriber.high_risk_threshold:
            if subscriber.notify_on_high:
                send_alert(type="high")
        
        elif risk_score_pct >= subscriber.medium_risk_threshold:
            if subscriber.notify_on_medium:
                send_alert(type="medium")
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New dependency added:** `apscheduler==3.10.4`

### 2. Configure Email Settings

Update your `.env` file:

```bash
# Email Configuration
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=your-app-password
```

**For Gmail:**
1. Go to Google Account settings
2. Enable 2-Step Verification
3. Generate an "App Password"
4. Use that app password in `ALERT_SENDER_PASSWORD`

### 3. Start the Application

The scheduler starts automatically when you run the application:

```bash
cd backend
uvicorn app.main:app --reload
```

You'll see in the logs:

```
🚀 Initializing backend services...
✅ Automated scheduler started (15-30 minute intervals)
✅ Backend services initialization completed

🔄 DATA UPDATE CYCLE #1
📊 Step 1: Updating protocol metrics...
✅ Updated 10 protocols
📈 Step 2: Recalculating risk scores...
✅ Updated 10 risk scores, 2 level changes
📧 Step 3: Checking subscriber alerts...
✅ Sent 3 alerts to 2 subscribers
✅ CYCLE COMPLETE
⏭️ Next update in: ~22 minutes
```

## API Usage Examples

### Check Scheduler Status

```bash
curl http://localhost:8000/monitoring/scheduler/status
```

Response:
```json
{
  "is_running": true,
  "update_count": 5,
  "last_update_time": "2025-10-27T10:30:00",
  "next_scheduled_run": "2025-10-27T10:52:00",
  "active_jobs": 1,
  "status_message": "Scheduler is running normally"
}
```

### Force Immediate Update

```bash
curl -X POST http://localhost:8000/monitoring/scheduler/force-update
```

### Subscribe to Alerts with Custom Thresholds

```bash
curl -X POST http://localhost:8000/email-alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "high_risk_threshold": 75.0,
    "medium_risk_threshold": 45.0,
    "notify_on_high": true,
    "notify_on_medium": true
  }'
```

### Check Subscriber Alert Status

```bash
curl http://localhost:8000/monitoring/alerts/subscriber/user@example.com/status
```

Response:
```json
{
  "subscriber_email": "user@example.com",
  "high_risk_threshold": 75.0,
  "medium_risk_threshold": 45.0,
  "notify_on_high": true,
  "notify_on_medium": true,
  "last_alert_sent": "2025-10-27T10:15:00",
  "protocols_above_high_threshold": 2,
  "protocols_above_medium_threshold": 5,
  "time_until_next_alert": "45 minutes"
}
```

### Send Test Alert

```bash
curl -X POST http://localhost:8000/monitoring/alerts/test/user@example.com
```

### Get Alert Statistics

```bash
curl http://localhost:8000/monitoring/alerts/statistics
```

Response:
```json
{
  "timestamp": "2025-10-27T10:30:00",
  "subscribers": {
    "total_active": 15,
    "verified": 12,
    "unverified": 3
  },
  "protocols": {
    "total_active": 25,
    "high_risk": 3,
    "medium_risk": 8,
    "low_risk": 14
  },
  "alerts": {
    "sent_last_hour": 7
  },
  "system_health": {
    "scheduler_running": true,
    "email_service_enabled": true
  }
}
```

## Customization

### Adjust Update Frequency

In `backend/app/services/automated_scheduler.py`:

```python
# Change the interval range (currently 15-30 minutes)
self.scheduler.add_job(
    self._run_data_update_cycle,
    trigger=IntervalTrigger(minutes=random.randint(15, 30)),  # Modify here
    ...
)
```

### Adjust Alert Cooldown

In `backend/app/services/subscriber_alert_service.py`:

```python
# Change cooldown period (currently 1 hour)
self.alert_cooldown = timedelta(hours=1)  # Modify here
```

### Adjust Data Change Ranges

In `backend/app/services/automated_scheduler.py`:

```python
# Currently: ±3% for TVL, ±8% for volume, ±2% for price
tvl_change = random.uniform(-0.03, 0.03)      # Modify range
volume_change = random.uniform(-0.08, 0.08)    # Modify range
price_change = random.uniform(-0.02, 0.02)     # Modify range
```

## Monitoring Dashboard

Access the API documentation at: http://localhost:8000/docs

Navigate to:
- **Monitoring** section for scheduler and alert controls
- **Email Alerts** section for subscriber management

## Troubleshooting

### Scheduler Not Starting

**Check logs:**
```bash
docker logs safefi-api -f
```

Look for:
```
❌ Failed to start automated scheduler: <error>
```

**Common issues:**
- Database connection failure
- Missing dependencies
- Port conflicts

### Emails Not Sending

1. **Check SMTP settings:**
```bash
curl http://localhost:8000/monitoring/alerts/statistics
```

Look for `email_service_enabled: true`

2. **Test email configuration:**
```bash
curl -X POST http://localhost:8000/monitoring/alerts/test/your-email@example.com
```

3. **Check Gmail app password:**
- Must use App Password, not regular password
- Enable 2-Step Verification first

### No Alerts Being Sent

1. **Check if subscribers are active and verified:**
```bash
curl http://localhost:8000/email-alerts/subscribers
```

2. **Check protocol risk scores:**
```bash
curl http://localhost:8000/api/v1/protocols
```

3. **Check if thresholds are too high:**
- Default high threshold: 70%
- Default medium threshold: 40%
- Adjust subscriber thresholds if needed

### Force Update Not Working

```bash
# Stop and restart scheduler
curl -X POST http://localhost:8000/monitoring/scheduler/stop
curl -X POST http://localhost:8000/monitoring/scheduler/start
```

## Production Deployment

### Environment Variables

Add to `.env.production`:

```bash
# Email Alerts
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=alerts@safefi.live
ALERT_SENDER_PASSWORD=<app-password>

# Scheduler
MONITOR_INTERVAL_SECONDS=900  # 15 minutes minimum
```

### Docker Compose

Already configured in `docker-compose.yml`:
```yaml
api:
  environment:
    EMAIL_ALERTS_ENABLED: ${EMAIL_ALERTS_ENABLED}
    SMTP_HOST: ${SMTP_HOST}
    SMTP_PORT: ${SMTP_PORT}
```

### Health Monitoring

Set up monitoring for:
```bash
# Scheduler health
curl https://api.safefi.live/monitoring/scheduler/status

# Alert system health
curl https://api.safefi.live/monitoring/alerts/statistics
```

Add to your monitoring dashboard or create alerts if:
- `is_running: false`
- `active_jobs: 0`
- `email_service_enabled: false`

## Testing the System

### 1. Start Application

```bash
uvicorn app.main:app --reload
```

### 2. Subscribe Test Email

```bash
curl -X POST http://localhost:8000/email-alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "high_risk_threshold": 60.0,
    "medium_risk_threshold": 30.0,
    "notify_on_high": true,
    "notify_on_medium": true
  }'
```

### 3. Send Test Alert

```bash
curl -X POST http://localhost:8000/monitoring/alerts/test/test@example.com
```

### 4. Force Update

```bash
curl -X POST http://localhost:8000/monitoring/scheduler/force-update
```

### 5. Check Logs

Watch for update cycle in logs:
```
🔄 DATA UPDATE CYCLE #1
📊 Step 1: Updating protocol metrics...
✅ Updated 10 protocols
📈 Step 2: Recalculating risk scores...
✅ Updated 10 risk scores, 2 level changes
   🔄 Uniswap: medium → high (72.5%)
   🔄 Aave: medium → low (35.2%)
📧 Step 3: Checking subscriber alerts...
✉️  Sent alert to test@example.com for Uniswap (72.5%)
✅ Sent 1 alerts to 1 subscribers
✅ CYCLE COMPLETE
⏭️ Next update in: ~18 minutes
```

## Summary

Your system now has:

✅ **Automatic updates** every 15-30 minutes
✅ **Realistic data changes** (small variations)
✅ **Risk score recalculation** after each update
✅ **Personalized alerts** per subscriber
✅ **Individual thresholds** for each subscriber
✅ **Spam prevention** with cooldown
✅ **Full monitoring** via API endpoints
✅ **Production-ready** with Docker support

The system runs automatically and requires no manual intervention!

## Support

For issues or questions:
- Check logs: `docker logs safefi-api -f`
- API docs: http://localhost:8000/docs
- Monitoring: http://localhost:8000/monitoring/scheduler/status
