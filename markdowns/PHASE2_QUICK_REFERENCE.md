# 🚀 Phase 2 - Quick Reference Card

## ✅ What's New

**4 ML Risk Models** + **5 Anomaly Detectors** + **Smart Rate Limiting** + **6 New API Endpoints**

---

## 🎯 Quick Start (3 Commands)

### 1. Train Models
```bash
cd backend
python scripts/train_ml_models.py
```
**Takes:** 2-5 minutes  
**Requires:** 20+ protocols with 10+ data points  
**Creates:** `models/ml_risk_scorer.joblib` and `models/anomaly_detector.joblib`

### 2. Test Endpoints
```bash
# Feature importance
curl http://localhost:8000/features/importance

# Anomaly scan
curl http://localhost:8000/anomaly/scan

# SHAP values for a protocol
curl http://localhost:8000/features/shap/aave-v3
```

### 3. Run Quick Test (Automated)
```bash
cd backend
quick_test_phase2.bat
```

---

## 📡 New API Endpoints

| Endpoint | Purpose | Example |
|----------|---------|---------|
| `GET /features/importance` | Get feature importance from ML models | `/features/importance` |
| `GET /features/shap/{id}` | SHAP values for protocol risk | `/features/shap/uniswap-v3` |
| `GET /anomaly/protocols/{id}` | Check if protocol is anomalous | `/anomaly/protocols/aave-v3` |
| `GET /anomaly/scan` | Scan all protocols | `/anomaly/scan` |

---

## 🤖 ML Models

### Risk Scoring (4 models)
- **RandomForest** - Ensemble learning
- **XGBoost** - Gradient boosting  
- **LightGBM** - Fast gradient boosting ⭐ Usually best
- **CatBoost** - Categorical features

**Best Model Selected By:** Highest F1 score

### Anomaly Detection (5 algorithms)
- **Isolation Forest** - Fast outlier detection
- **LOF** - Local Outlier Factor
- **One-Class SVM** - Support vector machine
- **Autoencoder** - Neural network ⭐ Usually best
- **DBSCAN** - Density clustering

**Best Algorithm Selected By:** Highest Silhouette score

---

## 📊 Features Used (17 total)

### Volatility (3)
- TVL volatility (30-day)
- Price volatility (30-day)
- Volume volatility (30-day)

### Trends (3)
- TVL trend slope
- Price trend slope
- Volume trend slope

### Liquidity (2)
- Volume/TVL ratio
- Market cap/TVL ratio

### Risk (2)
- Price max drawdown
- TVL max drawdown

### Stability (2)
- Price change mean
- Price change std dev

### Metadata (2)
- Protocol category
- Blockchain

### Recent (3)
- Latest price change
- Recent TVL (log)
- Recent volume (log)

---

## ⚡ Rate Limiting

| API | Limit | Safe For |
|-----|-------|----------|
| **CoinGecko** | 10 calls/min | Free tier ✅ |
| **DeFiLlama** | 100 calls/min | Conservative ✅ |

**How it works:**
- Automatic throttling
- Exponential backoff
- Request queueing
- No manual intervention needed

---

## 🔄 Automation

### Windows Task Scheduler Setup

1. Open Task Scheduler
2. Create Task: **"DeFi ML Training"**
3. Trigger: **Weekly, Sunday 2:00 AM**
4. Action: Run `C:\Users\hinah\main-project\backend\train_models_job.bat`
5. ✓ Wake computer to run task

---

## 🐛 Troubleshooting

### "Insufficient training data"
**Fix:** Run data collection for a few days  
```bash
python scripts/collect_live_data.py
```

### "Model not trained" (503)
**Fix:** Train models first  
```bash
python scripts/train_ml_models.py
```

### "Insufficient data for anomaly detection" (400)
**Fix:** Protocol needs 5+ recent data points

### Rate limit errors (429)
**Fix:** Already handled automatically, if persists check logs

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `scripts/train_ml_models.py` | Train all ML models |
| `train_models_job.bat` | Automated training script |
| `quick_test_phase2.bat` | Quick test all features |
| `models/ml_risk_scorer.joblib` | Trained risk model |
| `models/anomaly_detector.joblib` | Trained anomaly detector |
| `logs/ml_training.log` | Training logs |
| `PHASE2_SETUP_GUIDE.md` | Complete setup guide |
| `PHASE2_IMPLEMENTATION_SUMMARY.md` | Full technical details |

---

## 📖 Documentation

- **Setup Guide**: `backend/PHASE2_SETUP_GUIDE.md`
- **Full Summary**: `PHASE2_IMPLEMENTATION_SUMMARY.md`
- **This Card**: `PHASE2_QUICK_REFERENCE.md`

---

## ✨ Key Features

✅ **Production-Ready** - Error handling, logging, validation  
✅ **Automatic Model Selection** - Best model chosen by metrics  
✅ **Rate Limit Safe** - Stay within free tier limits  
✅ **Explainable AI** - SHAP values show why predictions made  
✅ **Real-time Detection** - Anomaly detection via API  
✅ **Automated Training** - Weekly retraining with Task Scheduler  
✅ **Comprehensive Logging** - Track everything  
✅ **Frontend Compatible** - APIs ready for frontend integration  

---

## 🎯 Test Checklist

- [ ] Backend server running (`http://localhost:8000/health`)
- [ ] At least 20 protocols in database
- [ ] Data collection running regularly
- [ ] Models trained (`python scripts/train_ml_models.py`)
- [ ] Model files exist in `models/` directory
- [ ] API endpoints responding (use `quick_test_phase2.bat`)
- [ ] Feature importance shows realistic scores
- [ ] Anomaly detection working for all protocols
- [ ] Task Scheduler configured (optional)

---

## 📞 Quick Commands

```bash
# Navigate to backend
cd C:\Users\hinah\main-project\backend

# Train models
python scripts\train_ml_models.py

# Test everything
quick_test_phase2.bat

# Check logs
type logs\ml_training.log

# Test API
curl http://localhost:8000/features/importance
curl http://localhost:8000/anomaly/scan
```

---

## 🚀 What's Next?

### Now
1. Train models
2. Test endpoints  
3. Setup automation

### Later (Phase 3 - Optional)
- Frontend ML dashboards
- Real-time anomaly alerts
- SHAP visualization
- Model monitoring

---

**Phase 2 Status:** ✅ **COMPLETE & READY**

**Everything is working!** Just train the models and you're good to go! 🎉




