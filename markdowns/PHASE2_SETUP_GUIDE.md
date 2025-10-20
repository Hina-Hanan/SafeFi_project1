# Phase 2 ML System - Setup & Usage Guide

## 🎯 Overview

Phase 2 implements a complete ML-powered risk assessment system with:
- **ML-based Risk Scoring**: 4 classification models (RandomForest, XGBoost, LightGBM, CatBoost)
- **Anomaly Detection**: 5 algorithms to detect unusual protocol behavior
- **Feature Importance**: SHAP values and feature analysis
- **Smart Rate Limiting**: Stay within CoinGecko free tier limits
- **Automated Training**: Weekly model retraining with latest data

---

## 📦 Installation

All ML dependencies were installed in Phase 1:
```bash
cd backend
pip install lightgbm catboost pyod hdbscan shap eli5 imbalanced-learn aiolimiter ratelimit slicer tqdm numba attrs tabulate
```

---

## 🚀 Quick Start

### 1. Initial Model Training

Train ML models with existing data (requires at least 20 protocols with 10+ data points each):

```bash
cd backend
python scripts/train_ml_models.py
```

This will:
- Collect historical data from database (last 90 days)
- Engineer 17 features per protocol
- Train 4 classification models for risk scoring
- Train 5 anomaly detection algorithms
- Save best models to `models/` directory
- Log performance metrics and feature importance

**Expected Output:**
```
🚀 ML MODEL TRAINING PIPELINE
================================================================================
TRAINING RISK SCORING MODELS
================================================================================
RandomForest         | F1=0.8523 | Accuracy=0.8421 | Precision=0.8612 | ...
XGBoost              | F1=0.8631 | Accuracy=0.8534 | Precision=0.8702 | ...
LightGBM             | F1=0.8745 | Accuracy=0.8642 | Precision=0.8814 | ...
CatBoost             | F1=0.8692 | Accuracy=0.8589 | Precision=0.8761 | ...

Best Model: LightGBM
F1 Score: 0.8745

Top 10 Most Important Features:
 1. tvl_vol_30                     : 0.1523
 2. price_vol_30                   : 0.1412
 3. max_drawdown                   : 0.1205
 ...

Model saved to: models/ml_risk_scorer.joblib

================================================================================
TRAINING ANOMALY DETECTION MODELS
================================================================================
Isolation Forest               | Anomalies=  18 (9.00%) | Silhouette=0.4523 ...
LOF                            | Anomalies=  22 (11.00%) | Silhouette=0.3912 ...
One-Class SVM                  | Anomalies=  19 (9.50%) | Silhouette=0.4201 ...
Autoencoder                    | Anomalies=  16 (8.00%) | Silhouette=0.4834 ...
DBSCAN                         | Anomalies=  21 (10.50%) | Silhouette=0.4102 ...

Best Algorithm: Autoencoder
Anomalies Detected: 16
Silhouette Score: 0.4834

Detector saved to: models/anomaly_detector.joblib

✅ TRAINING COMPLETED SUCCESSFULLY
```

### 2. Verify Model Files

Check that models were created:
```bash
dir models
```

You should see:
- `ml_risk_scorer.joblib` (Risk scoring model)
- `anomaly_detector.joblib` (Anomaly detection model)

### 3. Test New API Endpoints

#### Get Feature Importance
```bash
curl http://localhost:8000/features/importance
```

#### Detect Anomalies for a Protocol
```bash
curl http://localhost:8000/anomaly/protocols/aave-v3
```

#### Scan All Protocols for Anomalies
```bash
curl http://localhost:8000/anomaly/scan
```

#### Get SHAP Values for a Protocol
```bash
curl http://localhost:8000/features/shap/uniswap-v3
```

---

## 🤖 Automated Training

### Setup Windows Task Scheduler

1. Open **Task Scheduler** (search for it in Windows)

2. Create a new task:
   - **Name**: "DeFi ML Model Training"
   - **Description**: "Weekly training of ML risk scoring and anomaly detection models"

3. **Triggers** tab:
   - New trigger: Weekly, Sunday 2:00 AM

4. **Actions** tab:
   - Action: Start a program
   - Program: `C:\Users\hinah\main-project\backend\train_models_job.bat`
   - Start in: `C:\Users\hinah\main-project\backend`

5. **Conditions** tab:
   - ✓ Start only if computer is on AC power
   - ✓ Wake computer to run this task

6. **Settings** tab:
   - ✓ Allow task to be run on demand
   - ✓ If task fails, restart every: 1 hour

---

## 📊 API Endpoints Reference

### Anomaly Detection

#### `GET /anomaly/protocols/{protocol_id}`
Detect if a specific protocol exhibits anomalous behavior.

**Response:**
```json
{
  "protocol_id": "aave-v3",
  "protocol_name": "Aave V3",
  "is_anomaly": false,
  "anomaly_score": 0.23,
  "confidence": 0.91,
  "algorithm_used": "Autoencoder",
  "timestamp": "2025-10-04T20:45:00",
  "features_analyzed": ["tvl_vol_30", "price_vol_30", ...],
  "alert_level": "low"
}
```

#### `GET /anomaly/scan`
Scan all active protocols for anomalies.

**Response:**
```json
{
  "total_protocols": 20,
  "anomalies_detected": 2,
  "normal_protocols": 17,
  "errors": 1,
  "anomalous_protocols": [
    {
      "protocol_id": "some-protocol",
      "is_anomaly": true,
      "anomaly_score": 0.85,
      "alert_level": "high"
    }
  ]
}
```

### Feature Importance

#### `GET /features/importance`
Get feature importance from trained ML models.

**Response:**
```json
{
  "model_name": "LightGBM",
  "model_version": "1.0",
  "total_features": 17,
  "feature_importance": [
    {
      "feature_name": "tvl_vol_30",
      "importance_score": 0.1523,
      "rank": 1
    },
    ...
  ],
  "top_5_features": [
    {"feature": "tvl_vol_30", "importance": 0.1523},
    {"feature": "price_vol_30", "importance": 0.1412},
    ...
  ]
}
```

#### `GET /features/shap/{protocol_id}`
Get SHAP values explaining risk prediction for a protocol.

**Response:**
```json
{
  "protocol_id": "uniswap-v3",
  "protocol_name": "Uniswap V3",
  "model_used": "LightGBM",
  "shap_values": [
    {
      "feature": "tvl_vol_30",
      "shap_value": 0.23,
      "impact": "increases_risk",
      "magnitude": 0.23
    },
    {
      "feature": "liquidity_ratio",
      "shap_value": -0.15,
      "impact": "decreases_risk",
      "magnitude": 0.15
    },
    ...
  ],
  "top_5_contributors": [...]
}
```

---

## 🔧 Rate Limiting

### CoinGecko Free Tier Limits
- **10-50 calls/minute** (varies by endpoint)
- Our implementation: **10 calls/minute** (safe limit)
- Automatic exponential backoff on 429 errors
- Request queueing to prevent overload

### DeFiLlama Limits
- **300 calls/minute**
- Our implementation: **100 calls/minute** (conservative)

### Configuration

Rate limiters are automatically initialized in `app/services/rate_limiter.py`:
- `get_coingecko_rate_limiter()` - 10 calls per 60 seconds
- `get_defillama_rate_limiter()` - 100 calls per 60 seconds

All API calls in `DataCollectorService` now use rate limiting automatically.

---

## 📈 Feature Engineering

### 17 Features Used for ML Models:

1. **Volatility Features** (3):
   - `tvl_vol_30`: TVL volatility over 30 days
   - `price_vol_30`: Price volatility over 30 days
   - `volume_vol_30`: Volume volatility over 30 days

2. **Trend Features** (3):
   - `tvl_slope`: Linear trend of TVL
   - `price_slope`: Linear trend of price
   - `volume_slope`: Linear trend of volume

3. **Liquidity Features** (2):
   - `liquidity_ratio`: Volume/TVL ratio
   - `market_cap_to_tvl`: Market cap to TVL ratio

4. **Risk Features** (2):
   - `max_drawdown`: Maximum price drawdown from peak
   - `tvl_max_drawdown`: Maximum TVL drawdown

5. **Stability Features** (2):
   - `price_change_abs_mean`: Mean absolute price change
   - `price_change_std`: Price change standard deviation

6. **Metadata Features** (2):
   - `protocol_category`: Encoded category (DEX, Lending, etc.)
   - `protocol_chain`: Encoded blockchain

7. **Recent Performance** (3):
   - `recent_price_change`: Latest 24h price change
   - `recent_tvl`: Log-scaled recent TVL
   - `recent_volume`: Log-scaled recent volume

---

## 🎓 Model Details

### Risk Scoring Models

1. **RandomForest**
   - Ensemble of decision trees
   - Good for non-linear relationships
   - Provides feature importance

2. **XGBoost**
   - Gradient boosting
   - High performance
   - Handles imbalanced data well

3. **LightGBM**
   - Fast gradient boosting
   - Efficient memory usage
   - Often best F1 score

4. **CatBoost**
   - Handles categorical features natively
   - Robust to overfitting
   - Good default parameters

**Selection Criteria**: Highest F1 score from 5-fold cross-validation

### Anomaly Detection Algorithms

1. **Isolation Forest**
   - Isolates outliers using random trees
   - Fast and scalable
   - Good for high-dimensional data

2. **Local Outlier Factor (LOF)**
   - Density-based outlier detection
   - Finds local anomalies
   - Good for clustered data

3. **One-Class SVM**
   - Support vector machine approach
   - Learns decision boundary
   - Good for complex distributions

4. **Autoencoder** (Neural Network)
   - Learns normal patterns
   - Reconstruction error indicates anomalies
   - Best for complex relationships

5. **DBSCAN**
   - Density-based clustering
   - Finds noise points as anomalies
   - No need to specify contamination

**Selection Criteria**: Highest Silhouette score

---

## 🐛 Troubleshooting

### "Insufficient training data" Error

**Problem**: Not enough protocols with sufficient historical data.

**Solution**:
1. Run data collection for all protocols:
   ```bash
   python scripts/collect_live_data.py
   ```
2. Wait a few days to accumulate data
3. Retry training

### "Model not trained" Error (503)

**Problem**: Trying to use ML endpoints before training models.

**Solution**:
```bash
python scripts/train_ml_models.py
```

### "Insufficient data for anomaly detection" Error (400)

**Problem**: Protocol doesn't have enough recent data points.

**Solution**:
- Ensure data collection is running regularly
- Protocol needs at least 5 data points in last 30 days

### Rate Limit Errors (429)

**Problem**: Hitting CoinGecko API limits.

**Solution**:
- Rate limiting is automatic
- If persists, increase `period_seconds` in `rate_limiter.py`
- Consider upgrading to CoinGecko Pro API

---

## 📊 Monitoring

### Check Training Logs
```bash
type logs\ml_training.log
```

### Check Data Collection Logs
```bash
type logs\data_collection.log
```

### Verify Model Performance
```bash
curl http://localhost:8000/features/importance
```

Should show feature importance with scores > 0.

### Test Anomaly Detection
```bash
curl http://localhost:8000/anomaly/scan
```

Should return results for all active protocols.

---

## 🔄 Workflow

### Weekly Workflow (Automated)
1. **Sunday 2:00 AM**: Train ML models with latest data
2. **Every 15 minutes**: Collect fresh data from APIs
3. **Every 30 minutes**: Calculate risk scores using ML models
4. **Real-time**: Anomaly detection available via API

### Manual Workflow
1. **Seed protocols**: `python scripts/seed_real_protocols.py`
2. **Collect data**: `python scripts/collect_live_data.py`
3. **Train models**: `python scripts/train_ml_models.py`
4. **Calculate risks**: `python scripts/calculate_risks.py`
5. **Query APIs**: Use `/anomaly/*` and `/features/*` endpoints

---

## 🎯 Next Steps (Phase 3 - Optional)

- [ ] Frontend components for anomaly alerts
- [ ] Real-time anomaly notifications
- [ ] Historical anomaly tracking
- [ ] Feature importance visualization
- [ ] SHAP waterfall charts
- [ ] Model performance dashboard
- [ ] A/B testing framework
- [ ] Model drift detection

---

## 📚 Additional Resources

- **SHAP Documentation**: https://shap.readthedocs.io/
- **LightGBM Guide**: https://lightgbm.readthedocs.io/
- **PyOD (Anomaly Detection)**: https://pyod.readthedocs.io/
- **CoinGecko API**: https://www.coingecko.com/en/api/documentation

---

**Phase 2 Status**: ✅ Complete
**Models Trained**: 4 risk scoring + 5 anomaly detection
**API Endpoints**: 6 new endpoints for ML features
**Rate Limiting**: Smart limiting for CoinGecko & DeFiLlama
**Automation**: Batch scripts for Windows Task Scheduler




