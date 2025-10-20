# Backend-Frontend Data Issues - Diagnosis & Fix

## 🔴 Issues Identified

### 1. Backend Not Running
**Problem**: The backend server is not running
**Status**: Backend API at `http://localhost:8000` is not accessible

### 2. API Response Structure Mismatch
**Problem**: Frontend expects different data structure than backend provides

#### Backend Returns (v1/protocols.py):
```python
{
  "id": "uuid",
  "name": "Uniswap",
  "symbol": "UNI",
  "latest_risk_score": 0.65,
  "latest_risk_level": "medium",
  "latest_model_version": "v1.0",
  "latest_timestamp": "2024-01-01T00:00:00Z"
}
```

#### Frontend Expects (api.ts + components):
```javascript
{
  id: "uuid" OR protocol: { id: "uuid", name: "Uniswap" },
  latest_risk: {
    risk_score: 0.65,
    risk_level: "medium"
  },
  latest_metrics: {
    tvl_usd: 1000000,
    volume_24h_usd: 50000,
    price_change_24h: 2.5
  }
}
```

### 3. Missing Metrics in Protocol Response
**Problem**: Frontend expects `latest_metrics` but backend doesn't include it in the protocol list endpoint

### 4. Database Has Data
✅ **Good News**: Database has 4 protocols, 17 risk scores, and 369 metrics
- Uniswap
- Test DeFi Protocol 1
- Test Lending Protocol
- Test Yield Protocol

## 🔧 Solutions

### Solution 1: Start the Backend Server

```bash
cd backend
# Activate virtual environment (if using venv)
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Solution 2: Fix API Response Structure

We need to update the backend to match frontend expectations OR update frontend to match backend.

#### Option A: Fix Backend (Recommended)
Update `backend/app/api/v1/protocols.py` to include metrics and nest risk data:

```python
@router.get("", response_model=List[ProtocolWithRiskOut])
def list_protocols(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    protocols = db.query(Protocol).order_by(Protocol.name.asc()).offset(offset).limit(limit).all()
    protocol_ids = [p.id for p in protocols]
    
    # Get latest risk scores
    latest_scores = {}
    if protocol_ids:
        rows = (
            db.query(RiskScore)
            .filter(RiskScore.protocol_id.in_(protocol_ids))
            .order_by(RiskScore.protocol_id, RiskScore.timestamp.desc())
            .all()
        )
        for row in rows:
            if row.protocol_id not in latest_scores:
                latest_scores[row.protocol_id] = row
    
    # Get latest metrics
    latest_metrics = {}
    if protocol_ids:
        rows = (
            db.query(ProtocolMetric)
            .filter(ProtocolMetric.protocol_id.in_(protocol_ids))
            .order_by(ProtocolMetric.protocol_id, ProtocolMetric.timestamp.desc())
            .all()
        )
        for row in rows:
            if row.protocol_id not in latest_metrics:
                latest_metrics[row.protocol_id] = row
    
    result = []
    for p in protocols:
        rs = latest_scores.get(p.id)
        metric = latest_metrics.get(p.id)
        
        result.append({
            "id": p.id,
            "name": p.name,
            "symbol": p.symbol,
            "contract_address": p.contract_address,
            "category": p.category,
            "chain": p.chain,
            "is_active": p.is_active,
            "latest_risk": {
                "risk_score": rs.risk_score if rs else None,
                "risk_level": rs.risk_level if rs else None,
                "volatility_score": rs.volatility_score if rs else None,
                "liquidity_score": rs.liquidity_score if rs else None,
            } if rs else None,
            "latest_metrics": {
                "tvl_usd": float(metric.tvl) if metric and metric.tvl else None,
                "volume_24h_usd": float(metric.volume_24h) if metric and metric.volume_24h else None,
                "price_change_24h": metric.price_change_24h if metric else None,
            } if metric else None,
        })
    return result
```

#### Option B: Fix Frontend
Update `frontend/src/services/api.ts`:

```typescript
export const fetchProtocols = async () => {
  const { data } = await api.get('/protocols')
  // Transform backend format to expected format
  return data.map((protocol: any) => ({
    id: protocol.id,
    name: protocol.name,
    symbol: protocol.symbol,
    latest_risk: {
      risk_score: protocol.latest_risk_score,
      risk_level: protocol.latest_risk_level,
      volatility_score: protocol.volatility_score,
      liquidity_score: protocol.liquidity_score,
    },
    latest_metrics: null, // Metrics not included in list endpoint
  }))
}
```

### Solution 3: Add Health Endpoint Check

The frontend calls `/health` expecting:
```json
{
  "database_connected": true,
  "mlflow_connected": true,
  "timestamp": "2024-01-01T00:00:00Z",
  "total_protocols": 4,
  "total_metrics": 369,
  "total_risk_scores": 17
}
```

But backend returns:
```json
{
  "data": {"status": "ok"},
  "meta": {}
}
```

Update `backend/app/api/v1/health.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Protocol, ProtocolMetric, RiskScore
import os
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    try:
        total_protocols = db.query(Protocol).count()
        total_metrics = db.query(ProtocolMetric).count()
        total_risk_scores = db.query(RiskScore).count()
        database_connected = True
    except:
        database_connected = False
        total_protocols = 0
        total_metrics = 0
        total_risk_scores = 0
    
    # Check if MLflow is accessible
    mlflow_connected = os.path.exists("mlruns")  # Simple check
    
    return {
        "status": "ok",
        "database_connected": database_connected,
        "mlflow_connected": mlflow_connected,
        "timestamp": datetime.utcnow().isoformat(),
        "total_protocols": total_protocols,
        "total_metrics": total_metrics,
        "total_risk_scores": total_risk_scores,
    }
```

## 📝 Step-by-Step Fix Guide

### Step 1: Start Backend
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Verify Backend is Running
Open browser: `http://localhost:8000/docs`
- Should see FastAPI Swagger docs
- Try `/protocols` endpoint

### Step 3: Test Protocols Endpoint
```bash
curl http://localhost:8000/protocols
```

Expected: Array of protocols with data

### Step 4: Check Frontend Connection
- Frontend should be running at `http://localhost:5173`
- Check browser console for API errors
- Should now see protocol data

## 🎯 Quick Fix Commands

```bash
# Terminal 1: Start Backend
cd backend
.\venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --port 8000

# Terminal 2: Start Frontend
cd frontend
npm run dev

# Terminal 3: Test API
curl http://localhost:8000/protocols
curl http://localhost:8000/health
```

## ✅ Verification Checklist

- [ ] Backend server is running on port 8000
- [ ] Frontend server is running on port 5173
- [ ] `/health` endpoint returns status
- [ ] `/protocols` endpoint returns array of protocols
- [ ] Frontend console shows no CORS errors
- [ ] Frontend console shows no 404 errors
- [ ] Protocol cards appear in heatmap
- [ ] Risk data is visible on cards

## 🚨 Common Errors

### CORS Error
**Symptom**: Frontend shows CORS policy error
**Fix**: Ensure backend CORS middleware is configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection Refused
**Symptom**: `ERR_CONNECTION_REFUSED`
**Fix**: Backend is not running - start it!

### Empty Array
**Symptom**: `[]` returned from `/protocols`
**Fix**: Database might be empty - run seed data:
```bash
cd backend
python scripts/seed_data.py
```

### Data Structure Error
**Symptom**: `Cannot read property 'risk_score' of undefined`
**Fix**: API structure mismatch - apply Solution 2 above

## 📚 Related Files

- `backend/app/api/v1/protocols.py` - Protocol endpoints
- `backend/app/api/v1/health.py` - Health endpoint
- `backend/app/api/v1/schemas.py` - Response schemas
- `frontend/src/services/api.ts` - Frontend API calls
- `frontend/src/components/ProtocolHeatmap.tsx` - Renders protocols





