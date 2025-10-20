# 🚀 Starting Backend and Frontend Servers

## Quick Start (Both Servers)

### Windows PowerShell

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Linux/Mac

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step-by-Step Guide

### 1. Start Backend Server

#### Option A: With Virtual Environment (Recommended)
```powershell
# Navigate to backend directory
cd C:\Users\hinah\main-project\backend

# Activate virtual environment
.\venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Option B: Without Virtual Environment
```powershell
cd C:\Users\hinah\main-project\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXXX] using watchfiles
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend is Running:**
- Open browser: `http://localhost:8000/docs`
- You should see FastAPI Swagger documentation
- Try the `/health` endpoint - should return system status
- Try the `/protocols` endpoint - should return array of protocols

### 2. Start Frontend Server

```powershell
# Navigate to frontend directory
cd C:\Users\hinah\main-project\frontend

# Start development server
npm run dev
```

**Expected Output:**
```
  VITE v5.4.9  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

**Verify Frontend is Running:**
- Open browser: `http://localhost:5173`
- You should see the DeFi Risk Assessment Dashboard
- Protocol cards should appear in the heatmap
- No errors in browser console

## ✅ Verification Checklist

After starting both servers, verify:

1. **Backend Health Check**
   - Visit: `http://localhost:8000/health`
   - Should return JSON with:
     ```json
     {
       "status": "ok",
       "database_connected": true,
       "mlflow_connected": true,
       "total_protocols": 4,
       "total_metrics": 369,
       "total_risk_scores": 17
     }
     ```

2. **Backend Protocols Endpoint**
   - Visit: `http://localhost:8000/protocols`
   - Should return array of 4 protocols
   - Each protocol should have `latest_risk` and `latest_metrics` objects

3. **Frontend Dashboard**
   - Visit: `http://localhost:5173`
   - Should see dark themed dashboard
   - Protocol heatmap should show 4 protocols
   - No errors in browser console (F12)

4. **Frontend API Calls**
   - Open browser console (F12)
   - Network tab should show:
     - GET `/protocols` → 200 OK
     - GET `/health` → 200 OK
     - No CORS errors
     - No 404 errors

## 🔧 Troubleshooting

### Backend Won't Start

**Error: `ModuleNotFoundError: No module named 'fastapi'`**
```powershell
cd backend
pip install -r requirements.txt
```

**Error: `Address already in use`**
```powershell
# Port 8000 is already in use, use different port:
uvicorn app.main:app --port 8001 --reload
# Then update frontend .env: VITE_API_BASE_URL=http://localhost:8001
```

**Error: Database connection failed**
```powershell
# Check if PostgreSQL is running
# Windows: Services → PostgreSQL
# Linux: sudo systemctl status postgresql
# Mac: brew services list
```

### Frontend Won't Start

**Error: `Cannot find module`**
```powershell
cd frontend
npm install
npm run dev
```

**Error: `Port 5173 is already in use`**
```powershell
# Kill the process or use different port:
npm run dev -- --port 5174
```

### Frontend Shows No Data

**Symptom: Empty protocol list**

1. Check backend is running: `http://localhost:8000/docs`
2. Check browser console for errors (F12)
3. Verify API base URL in `frontend/.env` or `vite.config.ts`
4. Check CORS errors - backend should allow frontend origin

**Fix CORS if needed:**
In `backend/app/main.py`, ensure:
```python
allowed_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Data Structure Errors

**Symptom: `Cannot read property 'risk_score' of undefined`**

This should be fixed now. The backend has been updated to return:
```json
{
  "id": "uuid",
  "name": "Uniswap",
  "latest_risk": {
    "risk_score": 0.65,
    "risk_level": "medium"
  },
  "latest_metrics": {
    "tvl_usd": 1000000,
    "volume_24h_usd": 50000,
    "price_change_24h": 2.5
  }
}
```

If still seeing errors:
1. Hard refresh frontend: Ctrl+Shift+R
2. Clear browser cache
3. Restart both servers

## 📊 Expected Result

When both servers are running correctly, you should see:

### Backend Terminal:
```
INFO:     127.0.0.1:XXXXX - "GET /health HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /protocols HTTP/1.1" 200 OK
```

### Frontend Browser:
- **Dashboard Header**: DeFi Risk Assessment with pulsing logo
- **Metric Cards**: 4 cards showing System Health, Total Protocols, Risk Distribution, Model Performance
- **Protocol Heatmap**: 4 protocol cards with colors based on risk level:
  - Uniswap
  - Test DeFi Protocol 1
  - Test Lending Protocol
  - Test Yield Protocol
- **Interactive Elements**: Hover effects, animations, gradient buttons

### Browser Console (No Errors):
```
✓ Health check successful
✓ Protocols loaded: 4
✓ Risk scores loaded
✓ Metrics loaded
```

## 🎯 API Endpoints Available

Once backend is running, these endpoints are available:

### Health & System
- `GET /health` - System health and statistics
- `GET /` - API root information

### Protocols
- `GET /protocols` - List all protocols with latest risk & metrics
- `GET /protocols/{id}` - Get single protocol details
- `GET /protocols/{id}/metrics` - Get protocol metrics history
- `GET /protocols/{id}/risk` - Get protocol risk history

### Data Collection
- `POST /data/collect` - Trigger data collection from CoinGecko/DeFiLlama

### Risk Scoring
- `POST /risk/calculate-batch` - Calculate risk scores for protocols

### ML Models
- `GET /models/performance` - Get model performance metrics
- `POST /models/train` - Train ML models

### Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## 🔥 Production Deployment

For production, you'll want to:

### Backend:
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Frontend:
```bash
# Build for production
npm run build

# Serve with nginx or other web server
# Or use: npm run preview
```

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://defi_user:usersafety@localhost:5432/defi_risk_assessment
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
COINGECKO_API_KEY=your_api_key_here
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000
```

## ✨ You're All Set!

Both servers should now be running with:
- ✅ Backend serving API on http://localhost:8000
- ✅ Frontend serving UI on http://localhost:5173
- ✅ Data flowing correctly from backend to frontend
- ✅ Protocol cards displaying with risk levels and metrics
- ✅ Beautiful dark theme with animations

Enjoy your DeFi Risk Assessment Dashboard! 🚀





