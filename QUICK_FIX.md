# Quick Fix Guide

## ✅ Fix Applied: Missing Import

The import is already in the file `backend/app/api/v1/monitoring.py` at line 17:
```python
from app.services.email_alert_service import get_email_service
```

## 🔄 Now You Need to Restart the Backend

### Step 1: Stop Current Backend (if running)
Press `Ctrl+C` in the terminal running uvicorn

### Step 2: Restart Backend
```powershell
cd backend
uvicorn app.main:app --reload
```

You should see:
```
✅ Automated scheduler started (15-30 minute intervals)
```

### Step 3: Test the Fixed Endpoint

After restarting, test this command:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/monitoring/alerts/statistics"
```

Should work now! ✅

## 📧 Test Email Subscription

Use this command (PowerShell syntax):

```powershell
$body = @{
    email = "hinahanan003@gmail.com"
    high_risk_threshold = 60.0
    medium_risk_threshold = 35.0
    notify_on_high = $true
    notify_on_medium = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/email-alerts/subscribe" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

## 📊 Quick Test Script

Or use this one-liner test script:

```powershell
# Test scheduler
Invoke-RestMethod http://localhost:8000/monitoring/scheduler/status

# Test statistics (should work now!)
Invoke-RestMethod http://localhost:8000/monitoring/alerts/statistics

# Test test alert
Invoke-RestMethod -Method POST http://localhost:8000/monitoring/alerts/test/hinahanan003@gmail.com
```

## Summary

✅ **Import fixed** - Line 17 of monitoring.py
⏸️ **Need to restart** backend for changes to take effect
✅ **Then test** the endpoints

The issue was that the backend was running with the old code before the import was added. Once you restart, everything will work!

