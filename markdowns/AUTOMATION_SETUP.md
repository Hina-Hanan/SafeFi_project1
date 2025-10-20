# 🤖 Automated Data Collection Setup

## ✅ Automated Collection Every 15 Minutes

Your platform can now collect **LIVE data automatically** every 15 minutes!

---

## 📋 Quick Setup (5 Minutes)

### Method 1: Windows Task Scheduler (Recommended)

**I've created automated scripts for you:**
- ✅ `backend/collect_data_job.bat` - Collects live data
- ✅ `backend/calculate_risks_job.bat` - Calculates risk scores

**Follow these steps:**

---

## 🚀 Step-by-Step Instructions

### 1. Open Task Scheduler

**Windows Search** → Type: `Task Scheduler` → Open it

---

### 2. Create Data Collection Task

**In Task Scheduler:**

1. Click **"Create Basic Task..."** in right panel

2. **Name**: `DeFi Data Collection`
   - **Description**: `Collect live DeFi protocol data every 15 minutes`
   - Click **Next**

3. **Trigger**: Select **"Daily"**
   - Click **Next**
   - **Start**: Today's date
   - **Start time**: 00:00 (midnight)
   - **Recur every**: 1 days
   - Click **Next**

4. **Action**: Select **"Start a program"**
   - Click **Next**

5. **Program/Script**: 
   ```
   C:\Users\hinah\main-project\backend\collect_data_job.bat
   ```
   - Click **Next**

6. **Finish**: Check **"Open Properties dialog"**
   - Click **Finish**

7. **In Properties Dialog**:

   **Triggers Tab**:
   - Select the trigger → Click **Edit**
   - Check **"Repeat task every"**: `15 minutes`
   - **For a duration of**: `1 day`
   - Check **"Enabled"**
   - Click **OK**

   **Settings Tab**:
   - Uncheck **"Stop the task if it runs longer than"**
   - Check **"Run task as soon as possible after a scheduled start is missed"**
   - Check **"If the task fails, restart every"**: `5 minutes`
   - Click **OK**

---

### 3. Create Risk Calculation Task

**Repeat the same steps for risk calculation:**

1. **Name**: `DeFi Risk Calculation`
2. **Description**: `Calculate risk scores every 30 minutes`
3. **Program/Script**: 
   ```
   C:\Users\hinah\main-project\backend\calculate_risks_job.bat
   ```
4. **Repeat interval**: `30 minutes` (instead of 15)

---

## 🎯 What Happens Automatically

### Every 15 Minutes:
```
1. Connect to DeFiLlama API
2. Fetch latest TVL for all 20 protocols
3. Store metrics in PostgreSQL database
4. Log results
```

### Every 30 Minutes:
```
1. Read latest metrics from database
2. Calculate risk scores using algorithms
3. Store risk scores in database
4. Update dashboard data
```

### Your Dashboard:
- ✅ Auto-updates with fresh data
- ✅ Historical charts grow over time
- ✅ Risk scores recalculated regularly
- ✅ No manual intervention needed!

---

## 🔍 Verify It's Working

### Check Task Scheduler:

1. Open **Task Scheduler**
2. Click **Task Scheduler Library** (left panel)
3. Find your tasks: `DeFi Data Collection` and `DeFi Risk Calculation`
4. **Status** should show: **"Ready"** or **"Running"**
5. **Last Run Result** should show: **"The operation completed successfully (0x0)"**

### Check Logs:

**Windows Event Viewer**:
- Task Scheduler logs appear here
- See execution history

**Or check your backend terminal**:
- Watch for log messages appearing automatically

---

## 📊 Expected Results

### After 1 Hour (4 collections):
- Each protocol: **4 new metrics records**
- Each protocol: **2 new risk scores**
- Dashboard: More data points in charts

### After 1 Day (96 collections):
- Each protocol: **96 metrics records**
- Each protocol: **48 risk scores**
- Dashboard: Rich historical charts with trends

### After 1 Week:
- Each protocol: **672 metrics records**
- Robust risk trend analysis
- Clear volatility patterns
- Production-grade data depth

---

## 🛠️ Alternative Methods

### Method 2: Keep PowerShell Window Open

**Simple but requires keeping terminal open:**

```powershell
# Open PowerShell in backend directory
cd C:\Users\hinah\main-project\backend
.\venv\Scripts\Activate.ps1

# Run infinite loop (collects every 15 min)
while ($true) {
    Write-Host "`n[$(Get-Date)] Collecting data..." -ForegroundColor Cyan
    $env:PYTHONPATH="C:\Users\hinah\main-project\backend"
    python scripts\collect_live_data.py
    
    Write-Host "[$(Get-Date)] Calculating risks..." -ForegroundColor Yellow
    python scripts\calculate_risks.py
    
    Write-Host "[$(Get-Date)] Done! Sleeping for 15 minutes..." -ForegroundColor Green
    Start-Sleep -Seconds 900  # 15 minutes
}
```

**Pros**: Easy to start/stop
**Cons**: Must keep PowerShell window open

---

### Method 3: Python Script with Scheduler

**Create**: `backend/auto_updater.py`

```python
import schedule
import time
import subprocess
import os
from datetime import datetime

# Set environment
os.environ['PYTHONPATH'] = r'C:\Users\hinah\main-project\backend'

def collect_data():
    """Collect live data from APIs."""
    print(f"\n[{datetime.now()}] 🔄 Collecting data...")
    try:
        result = subprocess.run(
            ['python', 'scripts/collect_live_data.py'],
            cwd=r'C:\Users\hinah\main-project\backend',
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Data collection successful!")
        else:
            print(f"[{datetime.now()}] ❌ Error: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Exception: {e}")

def calculate_risks():
    """Calculate risk scores."""
    print(f"\n[{datetime.now()}] 🧮 Calculating risks...")
    try:
        result = subprocess.run(
            ['python', 'scripts/calculate_risks.py'],
            cwd=r'C:\Users\hinah\main-project\backend',
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[{datetime.now()}] ✅ Risk calculation successful!")
        else:
            print(f"[{datetime.now()}] ❌ Error: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Exception: {e}")

# Schedule jobs
schedule.every(15).minutes.do(collect_data)
schedule.every(30).minutes.do(calculate_risks)

# Run immediately on start
print("🚀 Starting automated data collection service...")
print("📊 Data collection: Every 15 minutes")
print("🎯 Risk calculation: Every 30 minutes")
print("Press Ctrl+C to stop\n")

collect_data()
calculate_risks()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**To run**:
```bash
cd backend
pip install schedule
python auto_updater.py
```

---

## 🎯 Recommended Setup

**For Development (Testing)**:
- Use **Method 2** (PowerShell loop)
- Easy to monitor and stop

**For Production (24/7 Operation)**:
- Use **Method 1** (Task Scheduler)
- Runs even after reboot
- No need to keep windows open

---

## 🔧 Troubleshooting

### Task Doesn't Run:

**Check:**
1. Is backend server running? (It should be separate!)
2. Is PostgreSQL running?
3. Check Task Scheduler logs
4. Try running `.bat` file manually to test

### Still Getting Module Errors:

**Fix the scripts permanently:**

Add to **top** of `collect_live_data.py`:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Rate Limiting Issues:

**DeFiLlama** has no rate limits ✅

**CoinGecko** free tier:
- Limit: 10-50 calls/min
- You'll see warnings (normal!)
- Upgrade to Pro if needed ($129/month)

---

## 📈 Monitor Your Automation

### Dashboard Will Show:

**After Setup**:
- More data points appearing automatically
- Risk scores updating
- Historical charts growing
- "Last Update" timestamp recent

### Database Check:

```bash
cd backend
python -c "
from app.database.connection import get_db
from app.database.models import ProtocolMetric, RiskScore

db = next(get_db())
metrics = db.query(ProtocolMetric).count()
risks = db.query(RiskScore).count()

print(f'Total Metrics: {metrics}')
print(f'Total Risk Scores: {risks}')
print('These numbers should increase over time!')
"
```

Run this every few hours to see growth!

---

## 💡 Pro Tips

### 1. Stagger the Tasks
- Data Collection: Every 15 min (00, 15, 30, 45)
- Risk Calculation: Every 30 min (05, 35)
- Prevents both running simultaneously

### 2. Add Email Alerts
- Task Scheduler can email on failure
- Configure in task properties

### 3. Log to File
- Modify `.bat` files to append to log:
  ```batch
  python scripts\collect_live_data.py >> logs\collection.log 2>&1
  ```

### 4. Database Backup
- Add weekly backup task
- Use `pg_dump` to export PostgreSQL

---

## 🎉 You're Done!

Your platform is now **fully automated**:

✅ **Real-time data** collected every 15 minutes
✅ **Risk scores** recalculated every 30 minutes  
✅ **Dashboard** updates automatically
✅ **Historical data** grows continuously
✅ **Production-ready** 24/7 operation

**Just set it up once and forget it!**

Your DeFi Risk Assessment platform is now a **true live production system**! 🚀

---

## 🆘 Quick Commands Reference

### Manual Run (Test):
```bash
cd C:\Users\hinah\main-project\backend
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="C:\Users\hinah\main-project\backend"
python scripts\collect_live_data.py
python scripts\calculate_risks.py
```

### Check Database Growth:
```bash
cd backend
python -c "from app.database.connection import get_db; from app.database.models import ProtocolMetric; print(f'Metrics: {next(get_db()).query(ProtocolMetric).count()}')"
```

### Stop Automation:
- Open Task Scheduler
- Right-click task → **Disable**

### Restart Automation:
- Right-click task → **Enable**
- Right-click task → **Run**

---

*Last Updated: 2025-10-04*
*Status: Automated Data Collection Ready* ✅





