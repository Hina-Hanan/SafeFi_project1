# Quick Start: Automated Alerts System

## What You Get

✅ Data updates **every 15-30 minutes** with small realistic changes (±1-3%)
✅ Automatic risk score recalculation
✅ **Personalized email alerts** for each subscriber
✅ Each subscriber sets their **own thresholds**
✅ Smart cooldown (1 hour) to prevent spam
✅ **Runs automatically** on startup

## 5-Minute Setup

### Step 1: Configure Email (Required)

Edit `.env`:

```bash
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=your-email@gmail.com
ALERT_SENDER_PASSWORD=your-app-password  # Use Gmail App Password
```

**Get Gmail App Password:**
1. Google Account → Security → 2-Step Verification (enable)
2. App Passwords → Generate
3. Copy password to `.env`

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt  # Includes apscheduler==3.10.4
```

### Step 3: Start Application

```bash
uvicorn app.main:app --reload
```

**You'll see:**
```
✅ Automated scheduler started (15-30 minute intervals)
🔄 DATA UPDATE CYCLE #1
✅ Updated 10 protocols
✅ Sent 2 alerts to 1 subscribers
⏭️ Next update in: ~22 minutes
```

## Test It Works

### 1. Subscribe with Custom Thresholds

```bash
curl -X POST http://localhost:8000/email-alerts/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "high_risk_threshold": 70.0,
    "medium_risk_threshold": 40.0,
    "notify_on_high": true,
    "notify_on_medium": true
  }'
```

### 2. Send Test Email

```bash
curl -X POST http://localhost:8000/monitoring/alerts/test/your@email.com
```

### 3. Force Immediate Update

```bash
curl -X POST http://localhost:8000/monitoring/scheduler/force-update
```

### 4. Check Status

```bash
curl http://localhost:8000/monitoring/scheduler/status
```

## How Subscriber Thresholds Work

Each subscriber can set their own thresholds:

```
Subscriber A:
  high_threshold: 80%
  medium_threshold: 50%
  → Gets alerts when protocols exceed their 80% or 50%

Subscriber B:
  high_threshold: 60%
  medium_threshold: 30%
  → Gets alerts when protocols exceed their 60% or 30%
```

**Same protocol, different alerts!**

## What Happens Every 15-30 Minutes

```
1. Update Data
   - TVL changes: ±3%
   - Volume changes: ±8%
   - Price changes: ±2%

2. Recalculate Risks
   - Update risk scores
   - Detect level changes (low/medium/high)

3. Check All Subscribers
   - Compare each protocol to each subscriber's thresholds
   - Send personalized alerts
   - Respect 1-hour cooldown per subscriber
```

## Monitor Everything

**API Docs:** http://localhost:8000/docs

**Key Endpoints:**
- `/monitoring/scheduler/status` - Scheduler status
- `/monitoring/alerts/statistics` - Alert statistics
- `/monitoring/alerts/subscriber/{email}/status` - Per-subscriber status
- `/email-alerts/subscribers` - All subscribers

## Customize

### Change Update Frequency

`backend/app/services/automated_scheduler.py`:
```python
# Line 64: Change from 15-30 to your preferred range
trigger=IntervalTrigger(minutes=random.randint(15, 30))
```

### Change Alert Cooldown

`backend/app/services/subscriber_alert_service.py`:
```python
# Line 30: Change from 1 hour
self.alert_cooldown = timedelta(hours=1)
```

### Change Data Variation

`backend/app/services/automated_scheduler.py`:
```python
# Lines 265-267: Adjust variation ranges
tvl_change = random.uniform(-0.03, 0.03)    # ±3%
volume_change = random.uniform(-0.08, 0.08)  # ±8%
price_change = random.uniform(-0.02, 0.02)   # ±2%
```

## Troubleshooting

### No emails sending?

1. **Check email config:**
```bash
curl http://localhost:8000/monitoring/alerts/statistics
# Look for: "email_service_enabled": true
```

2. **Test SMTP:**
```bash
curl -X POST http://localhost:8000/monitoring/alerts/test/your@email.com
```

3. **Check Gmail settings:**
   - Must use App Password
   - 2-Step Verification enabled
   - "Less secure apps" NOT needed

### Scheduler not running?

```bash
# Check status
curl http://localhost:8000/monitoring/scheduler/status

# Restart if needed
curl -X POST http://localhost:8000/monitoring/scheduler/stop
curl -X POST http://localhost:8000/monitoring/scheduler/start
```

### No alerts received?

1. **Check thresholds:**
```bash
curl http://localhost:8000/monitoring/alerts/subscriber/your@email.com/status
```

2. **Check if protocols exceed thresholds:**
```bash
curl http://localhost:8000/api/v1/protocols
```

3. **Check cooldown:**
```bash
# Shows "time_until_next_alert"
curl http://localhost:8000/monitoring/alerts/subscriber/your@email.com/status
```

## Production Deployment

### GCP/Docker

Already configured! Just set environment variables:

```bash
# In .env.production or docker-compose
EMAIL_ALERTS_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
ALERT_SENDER_EMAIL=alerts@safefi.live
ALERT_SENDER_PASSWORD=<app-password>
```

The scheduler starts automatically with the application.

### Health Monitoring

Add to your monitoring:

```bash
# Every 5 minutes, check:
curl https://api.safefi.live/monitoring/scheduler/status

# Alert if: is_running = false
```

## Files Created/Modified

**New Files:**
- `backend/app/services/subscriber_alert_service.py` - Personalized alerts
- `backend/app/services/automated_scheduler.py` - Auto scheduler
- `backend/app/api/v1/monitoring.py` - Monitoring endpoints
- `AUTOMATED_ALERTS_SETUP.md` - Full documentation

**Modified Files:**
- `backend/app/startup.py` - Added scheduler integration
- `backend/requirements.txt` - Added apscheduler
- `backend/app/api/v1/email_alerts.py` - Added imports

**Database:**
- Uses existing `EmailSubscriber` table (no migrations needed!)

## Summary

🎯 **Zero Manual Work Required**
- Starts automatically on app launch
- Runs continuously in background
- Handles all updates and alerts

🎯 **Personalized for Each User**
- Each subscriber sets own thresholds
- Gets alerts based on their preferences
- No spam with smart cooldown

🎯 **Production Ready**
- Comprehensive error handling
- Full monitoring and control
- Docker and cloud deployment ready

## Need Help?

📖 **Full Documentation:** `AUTOMATED_ALERTS_SETUP.md`
🚀 **API Docs:** http://localhost:8000/docs
📊 **Monitor:** http://localhost:8000/monitoring/scheduler/status
