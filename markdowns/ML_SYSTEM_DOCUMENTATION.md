# DeFi Risk Assessment ML System Documentation

## Overview

This document describes the complete Machine Learning Risk Scoring System implemented for the DeFi Risk Assessment project. The system provides production-ready ML-powered risk assessment with comprehensive MLflow integration.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Feature Eng.   │    │   ML Models     │
│                 │    │                 │    │                 │
│ • CoinGecko     │───▶│ • 12+ Features  │───▶│ • RandomForest  │
│ • DeFiLlama     │    │ • Volatility    │    │ • XGBoost       │
│ • PostgreSQL    │    │ • Liquidity     │    │ • LogisticReg   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MLflow        │    │   API Layer     │    │  Risk Scoring   │
│                 │    │                 │    │                 │
│ • Experiments   │◀───│ • Training      │◀───│ • Individual    │
│ • Model Registry│    │ • Prediction    │    │ • Batch         │
│ • Tracking      │    │ • Performance   │    │ • Historical    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Risk Calculator Service (`app/services/risk_calculator.py`)

The main service class that orchestrates the entire ML pipeline:

**Key Features:**
- Advanced feature engineering with 12+ risk indicators
- Multiple ML algorithms with hyperparameter tuning
- MLflow integration for experiment tracking
- Real-time predictions with confidence scores
- Batch processing with performance monitoring

**Main Methods:**
- `train_models()`: Train and compare multiple ML models
- `predict_protocol()`: Generate risk prediction for a single protocol
- `predict_batch()`: Batch risk calculation for all protocols
- `get_model_performance_metrics()`: Retrieve MLflow metrics

### 2. Feature Engineering

The system generates 12 sophisticated risk indicators:

#### Volatility Measures
- `tvl_vol_30`: 30-day TVL volatility (standard deviation)
- `price_vol_30`: 30-day price volatility
- `volume_vol_30`: 30-day volume volatility
- `mc_vol_30`: 30-day market cap volatility

#### Trend Analysis
- `price_slope`: Price trend slope (30-day linear regression)
- `tvl_slope`: TVL trend slope
- `tvl_trend_7`: Short-term TVL trend (7-day)
- `price_momentum`: 7-day price momentum

#### Liquidity & Stability
- `liquidity_ratio_30`: Volume/TVL ratio (30-day average)
- `volume_consistency`: Inverse coefficient of variation
- `market_cap_stability`: Inverse volatility measure
- `drawdown_risk`: Maximum drawdown from peak

### 3. ML Models

Three algorithms are trained and compared:

#### Random Forest Classifier
- **Hyperparameters**: n_estimators, max_depth, min_samples_split, min_samples_leaf
- **Strengths**: Feature importance, robust to outliers
- **Use case**: Interpretable risk assessment

#### XGBoost Classifier  
- **Hyperparameters**: n_estimators, max_depth, learning_rate, subsample
- **Strengths**: High performance, handles missing data
- **Use case**: Maximum predictive accuracy

#### Logistic Regression
- **Hyperparameters**: C, penalty, solver
- **Strengths**: Fast, probabilistic outputs
- **Use case**: Baseline comparison, fast inference

### 4. MLflow Integration

Comprehensive experiment tracking and model management:

#### Experiment Tracking
- Dataset metadata (size, features, distribution)
- Hyperparameter grids and best parameters
- Cross-validation scores and test metrics
- Classification reports and confusion matrices

#### Model Registry
- Automatic model registration with versioning
- Model staging (None/Staging/Production)
- Model artifacts and preprocessing pipelines
- Input/output signatures and examples

#### Performance Monitoring
- Batch prediction metrics
- Risk level distribution tracking
- Model drift detection capabilities
- A/B testing framework ready

## API Endpoints

### Model Management

#### `POST /models/train`
Train multiple ML models with hyperparameter tuning.

**Response:**
```json
{
  "success": true,
  "message": "Successfully trained 3 models",
  "models": [
    {
      "model_name": "rf",
      "accuracy": 0.85,
      "precision": 0.84,
      "recall": 0.85,
      "f1": 0.84,
      "best_params": {"n_estimators": 200, "max_depth": 10},
      "run_id": "abc123",
      "model_uri": "models:/risk_scoring_rf/1"
    }
  ],
  "best_model": "rf",
  "training_time": "45.2 seconds"
}
```

#### `GET /models/performance`
Get comprehensive model performance metrics.

**Response:**
```json
{
  "experiment_name": "risk_scoring",
  "total_runs": 15,
  "recent_runs": [...],
  "model_registry": {
    "risk_scoring_rf": {
      "latest_version": "3",
      "stage": "Production",
      "creation_time": 1699123456789
    }
  },
  "performance_summary": {
    "avg_f1_score": 0.82,
    "best_f1_score": 0.87,
    "recent_trend": "improving"
  }
}
```

#### `GET /models/compare/{model_name}`
Compare different versions of a specific model.

### Risk Scoring

#### `GET /risk/protocols/{protocol_id}/risk-details`
Get detailed risk analysis for a protocol.

**Response:**
```json
{
  "protocol_id": "abc-123",
  "risk_score": 0.65,
  "risk_level": "medium",
  "confidence": 0.89,
  "features": {
    "tvl_vol_30": 0.12,
    "price_vol_30": 0.25,
    "liquidity_ratio_30": 0.08,
    ...
  },
  "model_version": "risk_scoring_rf_v3",
  "explanation": {
    "method": "ml_model",
    "feature_importance": {
      "price_vol_30": 0.23,
      "tvl_vol_30": 0.19,
      ...
    },
    "key_risk_drivers": [
      {
        "feature": "price_vol_30",
        "value": 0.25,
        "importance": 0.23,
        "interpretation": "Price volatility is high"
      }
    ]
  }
}
```

#### `POST /risk/calculate-batch`
Calculate risk scores for all active protocols.

**Request:**
```json
{
  "protocol_ids": ["abc-123", "def-456"],  // optional
  "force_refresh": false
}
```

#### `GET /risk/protocols/{protocol_id}/history`
Get historical risk scores for trend analysis.

**Parameters:**
- `limit`: Number of records (1-200, default: 50)
- `days`: Days of history (1-365, default: 30)

## Database Schema

### Risk Scores Table
```sql
CREATE TABLE risk_scores (
    id UUID PRIMARY KEY,
    protocol_id UUID REFERENCES protocols(id),
    risk_level VARCHAR(10) NOT NULL,  -- 'low', 'medium', 'high'
    risk_score FLOAT NOT NULL,        -- 0.0 to 1.0
    volatility_score FLOAT,           -- Optional component scores
    liquidity_score FLOAT,
    model_version VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_risk_scores_protocol_time ON risk_scores(protocol_id, timestamp);
```

## Deployment & Configuration

### Docker Compose Setup

The system includes MLflow server configuration:

```yaml
services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.16.2
    command: mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri /mlflow --default-artifact-root /mlflow
    ports:
      - "5000:5000"
    volumes:
      - mlruns:/mlflow

  api:
    environment:
      MLFLOW_TRACKING_URI: http://mlflow:5000
```

### Environment Variables

```bash
# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000

# Database Configuration
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/defi_risk

# Logging Configuration
LOG_LEVEL=INFO
```

### Dependencies

Key Python packages (see `requirements.txt`):
```
mlflow==2.16.2
scikit-learn==1.5.2
xgboost==2.1.1
pandas==2.2.3
numpy==2.1.2
joblib==1.4.2
```

## Usage Examples

### 1. Training Models

```python
from app.services.risk_calculator import RiskCalculatorService

# Initialize service
service = RiskCalculatorService()

# Train models with automatic MLflow tracking
performances = service.train_models()

# Get best model
best_model = max(performances, key=lambda p: p.f1)
print(f"Best model: {best_model.model_name} (F1: {best_model.f1:.4f})")
```

### 2. Single Protocol Risk Assessment

```python
# Get detailed risk prediction
prediction = service.predict_protocol("protocol-id-123")

print(f"Risk Level: {prediction.risk_level}")
print(f"Risk Score: {prediction.risk_score:.4f}")
print(f"Confidence: {prediction.confidence:.4f}")
print(f"Model: {prediction.model_version}")

# Access feature values
print(f"Price Volatility: {prediction.features['price_vol_30']:.4f}")

# Get explanation
if prediction.explanation.get('key_risk_drivers'):
    for driver in prediction.explanation['key_risk_drivers']:
        print(f"- {driver['interpretation']}")
```

### 3. Batch Processing

```python
# Process all protocols
results = service.predict_batch()

print(f"Processed {len(results)} protocols")

# Analyze risk distribution
risk_levels = [r['risk_level'] for r in results]
from collections import Counter
distribution = Counter(risk_levels)
print(f"Risk distribution: {distribution}")
```

### 4. API Usage

```bash
# Train models
curl -X POST http://localhost:8000/models/train

# Get risk assessment
curl http://localhost:8000/risk/protocols/abc-123/risk-details

# Batch calculation
curl -X POST http://localhost:8000/risk/calculate-batch \
  -H "Content-Type: application/json" \
  -d '{}'

# Check model performance
curl http://localhost:8000/models/performance
```

## Testing

Run the comprehensive test suite:

```bash
cd backend
python test_ml_system.py
```

The test suite validates:
- Feature engineering pipeline
- Model training and evaluation
- Risk prediction accuracy
- Batch processing performance
- API endpoint functionality
- MLflow integration

## Performance Considerations

### Scalability
- **Feature Engineering**: Optimized pandas operations with vectorization
- **Model Training**: Parallel hyperparameter search with `n_jobs=-1`
- **Batch Prediction**: Chunked processing for large protocol sets
- **Database**: Indexed queries on protocol_id and timestamp

### Monitoring
- **MLflow Tracking**: All experiments and metrics logged
- **Performance Metrics**: Training time, prediction latency, accuracy trends
- **Data Quality**: Missing data handling and validation
- **Error Handling**: Comprehensive logging and graceful degradation

### Caching
- **Model Loading**: Cached production models in memory
- **Feature Computation**: Efficient rolling window calculations
- **Database Queries**: Connection pooling and prepared statements

## Security & Compliance

### Data Protection
- **Input Validation**: All API inputs sanitized and validated
- **SQL Injection**: Parameterized queries with SQLAlchemy ORM
- **Access Control**: Protocol-level data access restrictions

### Model Security
- **Model Versioning**: Immutable model artifacts in MLflow
- **Audit Trail**: Complete lineage from data to predictions
- **Rollback Capability**: Easy reversion to previous model versions

## Troubleshooting

### Common Issues

1. **No Data for Training**
   - Ensure data collection service is running
   - Check database connectivity
   - Verify protocol metrics are being collected

2. **MLflow Connection Errors**
   - Verify MLflow server is running on port 5000
   - Check `MLFLOW_TRACKING_URI` environment variable
   - Ensure network connectivity between services

3. **Low Model Performance**
   - Check data quality and completeness
   - Verify feature engineering logic
   - Consider collecting more historical data

4. **Prediction Errors**
   - Ensure sufficient data points (minimum 30 days)
   - Check for missing or invalid metric values
   - Verify model registry contains trained models

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger('app.services.risk_calculator').setLevel(logging.DEBUG)
```

Check MLflow UI:
```bash
# Open browser to http://localhost:5000
# View experiments, runs, and model registry
```

## Future Enhancements

### Planned Features
1. **Real-time Model Monitoring**: Automatic drift detection
2. **Advanced Feature Engineering**: Technical indicators, sentiment analysis
3. **Ensemble Methods**: Model stacking and blending
4. **Explainable AI**: SHAP values and LIME explanations
5. **Auto-ML**: Automated feature selection and model optimization

### Scalability Improvements
1. **Distributed Training**: Dask or Ray for large-scale training
2. **Streaming Predictions**: Real-time risk score updates
3. **Model Serving**: Dedicated inference servers
4. **Feature Store**: Centralized feature management

---

## Support

For technical support or questions about the ML system:
1. Check the logs in `/var/log/defi-risk/`
2. Review MLflow UI for experiment details
3. Run the test suite to validate system health
4. Contact the development team with specific error messages

This ML Risk Scoring System provides a robust, production-ready foundation for DeFi protocol risk assessment with comprehensive monitoring, versioning, and explainability features.
