# 🚀 Production Deployment Guide

## Transform to Real-Time Live Platform

Your DeFi Risk Assessment platform is **already production-ready** with real API integrations! This guide shows you how to deploy with **real protocols and live data**.

---

## 🎯 Quick Production Setup (One Command!)

```bash
cd backend
python scripts/production_setup.py
```

This will:
1. ✅ Remove test protocols
2. ✅ Add **20 real DeFi protocols** (Uniswap, Aave, Lido, etc.)
3. ✅ Collect live data from CoinGecko & DeFiLlama
4. ✅ Calculate real-time risk scores
5. ✅ Verify system health

**Time: ~5 minutes** (depending on API rate limits)

---

## 📊 Real Protocols Included

### DEX (Decentralized Exchanges)
- 🦄 **Uniswap** (UNI) - Largest DEX
- 🥞 **PancakeSwap** (CAKE) - BSC leader
- 🍣 **SushiSwap** (SUSHI) - Multi-chain DEX
- 🌊 **Curve** (CRV) - Stablecoin DEX
- ⚖️ **Balancer** (BAL) - Weighted pools
- 1️⃣ **1inch** (1INCH) - DEX aggregator
- And more...

### Lending & Borrowing
- 👻 **Aave** (AAVE) - #1 lending protocol
- 🏦 **Compound** (COMP) - Algorithmic lending
- 📜 **MakerDAO** (MKR) - DAI stablecoin
- 🔥 **Frax Finance** (FXS) - Fractional stablecoin

### Liquid Staking
- 🌈 **Lido** (LDO) - Largest liquid staking
- 🚀 **Rocket Pool** (RPL) - Decentralized staking

### Yield Aggregators
- 💰 **Yearn Finance** (YFI) - Yield optimization
- ⚙️ **Convex Finance** (CVX) - Curve boosting

### Derivatives
- 📈 **dYdX** (DYDX) - Perpetuals
- 🎯 **GMX** (GMX) - Decentralized perps

### Bridges
- ⭐ **Stargate Finance** (STG) - Omnichain bridge
- 🌉 **Synapse** (SYN) - Cross-chain bridge

### Total: **20+ major protocols** across all categories!

---

## 🔄 Manual Setup (Step-by-Step)

If you prefer manual control:

### Step 1: Add Real Protocols
```bash
cd backend
python scripts/seed_real_protocols.py
```

### Step 2: Collect Live Data
```bash
python scripts/collect_live_data.py
```

### Step 3: Calculate Risk Scores
```bash
python scripts/calculate_risks.py
```

---

## ⏰ Automated Data Refresh (Production)

For a **truly live platform**, set up automated data collection:

### Option 1: Windows Task Scheduler

**Create Task for Data Collection (Every 15 minutes):**
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Every 15 minutes
4. Action: Start Program
   - Program: `C:\Users\hinah\main-project\backend\venv\Scripts\python.exe`
   - Arguments: `scripts/collect_live_data.py`
   - Start in: `C:\Users\hinah\main-project\backend`

**Create Task for Risk Calculation (Every 30 minutes):**
- Same steps but run `scripts/calculate_risks.py`

### Option 2: Python Scheduler (Recommended)

Create `backend/scripts/scheduler.py`:

```python
"""
Production scheduler for automated data refresh.
Runs continuously and updates data every 15 minutes.
"""
import asyncio
import schedule
import time
import logging
from collect_live_data import main as collect_data
from calculate_risks import main as calculate_risks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def job_collect():
    logger.info("🔄 Running scheduled data collection...")
    asyncio.run(collect_data())

def job_risks():
    logger.info("🧮 Running scheduled risk calculation...")
    calculate_risks()

# Schedule jobs
schedule.every(15).minutes.do(job_collect)
schedule.every(30).minutes.do(job_risks)

logger.info("⏰ Scheduler started! Press Ctrl+C to stop.")
logger.info("📊 Data collection: Every 15 minutes")
logger.info("🧮 Risk calculation: Every 30 minutes")

# Run once immediately
job_collect()
job_risks()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
```

**Install scheduler:**
```bash
pip install schedule
```

**Run scheduler:**
```bash
python scripts/scheduler.py
```

### Option 3: Cron Jobs (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add these lines:
*/15 * * * * cd /path/to/backend && ./venv/bin/python scripts/collect_live_data.py
*/30 * * * * cd /path/to/backend && ./venv/bin/python scripts/calculate_risks.py
```

---

## 🌐 Production Environment Variables

Create `backend/.env` for production:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/defi_risk_prod

# API Keys (for higher rate limits)
COINGECKO_API_KEY=your_coingecko_pro_key_here
DEFILLAMA_API_KEY=optional_defillama_key

# MLflow (optional)
MLFLOW_TRACKING_URI=http://localhost:5001

# Server
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=INFO

# Database Connection Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

---

## 🔑 API Keys (Recommended for Production)

### CoinGecko Pro API
- **Free tier**: 10-50 calls/minute
- **Pro tier**: 500+ calls/minute, better for 20+ protocols
- Get key: https://www.coingecko.com/en/api/pricing

### DeFiLlama
- No API key needed
- Public API with generous rate limits

---

## 🏗️ Production Deployment

### Backend Deployment

**Option 1: Gunicorn (Recommended)**
```bash
cd backend
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Option 2: Docker**
```dockerfile
# backend/Dockerfile (already exists)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

```bash
docker build -t defi-risk-backend .
docker run -p 8000:8000 --env-file .env defi-risk-backend
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Serve with nginx or deploy to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
# - Your own server with nginx
```

---

## ✅ Production Checklist

### Pre-Deployment
- [ ] Run `python scripts/production_setup.py`
- [ ] Verify all protocols have data
- [ ] Test all API endpoints
- [ ] Set up automated data refresh
- [ ] Configure production environment variables
- [ ] Get CoinGecko Pro API key (optional but recommended)

### Security
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Enable database backups
- [ ] Use environment variables (never commit secrets)

### Monitoring
- [ ] Set up health check monitoring
- [ ] Configure error logging (Sentry, etc.)
- [ ] Monitor API rate limits
- [ ] Track database performance
- [ ] Set up uptime monitoring

### Performance
- [ ] Database connection pooling enabled
- [ ] CDN for frontend assets
- [ ] API response caching
- [ ] Database indexes optimized
- [ ] Load balancer (if needed)

---

## 📊 Expected Results

After production setup, your dashboard will show:

**Real Protocols**: 20+ major DeFi protocols
**Live Data**: Updated every 15 minutes
- TVL from DeFiLlama
- Prices from CoinGecko
- Market caps & changes
- Volume data

**Real Risk Scores**: ML-calculated every 30 minutes
- Volatility analysis
- Liquidity assessment
- Historical trends
- Risk classifications

---

## 🔍 Verify Production Setup

### Check Database
```bash
python -c "from app.database.connection import managed_session; from app.database.models import Protocol; with managed_session() as db: print(f'Protocols: {db.query(Protocol).count()}')"
```

Expected: `Protocols: 20+`

### Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Protocols with real data
curl http://localhost:8000/protocols

# Should see Uniswap, Aave, Lido, etc.
```

### Check Dashboard
Open http://localhost:5173 and verify:
- ✅ 20+ protocol cards displayed
- ✅ Real protocol names (Uniswap, Aave, etc.)
- ✅ TVL values showing
- ✅ Risk scores displayed
- ✅ Database status: Connected

---

## 🚀 Going Live

### 1. Start Backend (Production)
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 2. Start Scheduler (Background)
```bash
# In separate terminal
python scripts/scheduler.py
```

### 3. Deploy Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting
```

### 4. Monitor
- Check logs regularly
- Monitor API rate limits
- Track database growth
- Watch for errors

---

## 💡 Pro Tips

1. **CoinGecko API Key**: Get Pro plan for 20+ protocols
2. **Database Backups**: Run daily backups
3. **Error Monitoring**: Use Sentry or similar
4. **Caching**: Add Redis for API responses
5. **CDN**: Use CloudFlare for static assets
6. **Load Balancer**: Use nginx for multiple backend instances
7. **Health Checks**: Monitor uptime with UptimeRobot
8. **Alerts**: Set up Discord/Slack alerts for failures

---

## 🆘 Troubleshooting

### "Rate limit exceeded"
- Get CoinGecko Pro API key
- Reduce collection frequency
- Add delays between requests

### "No data for some protocols"
- Check API responses manually
- Verify contract addresses
- Some protocols may not be on CoinGecko

### "Risk scores not updating"
- Check if data collection ran successfully
- Verify database has recent metrics
- Check risk calculation logs

---

## 📚 Additional Resources

- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [DeFiLlama API Docs](https://defillama.com/docs/api)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Optimization](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

## 🎉 Success!

Your DeFi Risk Assessment platform is now:
- ✅ **Production-ready** with real protocols
- ✅ **Real-time** with live data collection
- ✅ **Automated** with scheduled updates
- ✅ **Scalable** with proper architecture
- ✅ **Professional** with error handling

**You're ready to launch!** 🚀





