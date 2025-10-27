<!-- f6d52062-fe07-4a8f-b061-5368b257fa45 850997f4-986f-4716-a7bc-69b6e2878e46 -->
# SafeFi DeFi Risk Assessment Platform - Complete Documentation

## Document Structure

Create a comprehensive markdown documentation file (`SAFEFI_PRODUCTION_DOCUMENTATION.md`) covering:

### 1. Executive Summary (2-3 pages)

- Project overview and mission
- Key capabilities and value proposition
- System architecture at-a-glance
- Production metrics and performance
- Target users and use cases

### 2. System Architecture (4-5 pages)

- **Technology Stack**
  - Backend: FastAPI (Python 3.11+), PostgreSQL, SQLAlchemy ORM
  - Frontend: React + TypeScript, Material-UI, TanStack Query
  - ML/AI: Scikit-learn, XGBoost, MLflow, Ollama (TinyLlama)
  - Infrastructure: GCP VM, Nginx reverse proxy, SSL/TLS (Let's Encrypt)
  - Monitoring: MLflow tracking, structured logging

- **Architecture Diagram** (text-based)
  - Frontend (safefi.live) → Nginx → Backend API (api.safefi.live)
  - Backend → PostgreSQL database
  - Backend → External APIs (CoinGecko, DeFiLlama)
  - Backend → MLflow tracking server
  - Backend → Ollama LLM service
  - Backend → Vector store (FAISS)

- **Data Flow**
  - Real-time data collection workflow
  - Risk calculation pipeline
  - ML model training and inference
  - RAG-powered AI assistant flow

### 3. Real Data Sources & Collection (3-4 pages)

- **External API Integrations**
  - **CoinGecko API**: Price data, market cap, 24h price changes
    - Rate limiting: ~3 req/sec
    - Contract-based resolution for accuracy
    - Fallback to symbol/name search

  - **DeFiLlama API**: TVL (Total Value Locked) data
    - Protocol slug resolution
    - Real-time TVL snapshots
    - Multi-chain support

- **Data Collection Workflow**
  - Automated collection via `DataCollectorService`
  - Retry logic with exponential backoff
  - Rate limiting per API provider
  - Data validation and transformation
  - Storage in `protocol_metrics` table

- **Monitored Protocols** (20 real DeFi protocols)
  - **DEX**: Uniswap, PancakeSwap, SushiSwap, Curve, Balancer, 1inch, Trader Joe, Osmosis
  - **Lending**: Aave, Compound, MakerDAO, Frax Finance
  - **Yield**: Yearn Finance, Convex Finance
  - **Staking**: Lido, Rocket Pool
  - **Derivatives**: dYdX, GMX
  - **Bridges**: Stargate Finance, Synapse

### 4. Database Schema & Risk Features (4-5 pages)

- **Core Tables**
  - `protocols`: Protocol metadata, contract addresses, chains
  - `protocol_metrics`: Time-series market data
  - `risk_scores`: ML-generated risk assessments
  - `email_subscribers`: Alert subscription management

- **Risk Calculation Features** (12+ engineered features)

**Volatility Indicators** (40% weight):

  - `tvl_vol_30`: 30-day TVL volatility (std dev)
  - `price_vol_30`: 30-day price volatility
  - `volume_vol_30`: 30-day trading volume volatility
  - `mc_vol_30`: 30-day market cap volatility
  - **Impact**: Higher volatility → Higher risk score

**Trend Analysis** (20% weight):

  - `price_slope`: 30-day price trend (linear regression)
  - `tvl_slope`: 30-day TVL trend
  - `tvl_trend_7`: 7-day short-term TVL trend
  - `price_momentum`: 7-day price momentum
  - **Impact**: Negative trends → Higher risk score

**Liquidity Metrics** (30% weight):

  - `liquidity_ratio_30`: Volume/TVL ratio (higher = more liquid)
  - `volume_consistency`: Inverse coefficient of variation
  - **Impact**: Lower liquidity → Higher risk score

**Stability Indicators** (10% weight):

  - `market_cap_stability`: Inverse of market cap volatility
  - `drawdown_risk`: Maximum drawdown from peak
  - **Impact**: Lower stability → Higher risk score

- **Feature Engineering Process**
  - Rolling window calculations (7-day, 30-day)
  - Forward-fill for missing values
  - Slope calculation via linear regression
  - Normalization and scaling (StandardScaler)

### 5. Machine Learning Models (5-6 pages)

- **ML Risk Scoring System** (`RiskCalculatorService`)

**Model Training Pipeline**:

  1. Data loading from PostgreSQL
  2. Feature engineering (12+ features)
  3. Synthetic label generation using advanced heuristics
  4. Train/test split (75/25) with stratification
  5. Hyperparameter tuning via GridSearchCV
  6. Cross-validation (5-fold StratifiedKFold)
  7. Model selection based on weighted F1 score
  8. MLflow tracking and model registry

**Algorithms Evaluated**:

  - **Logistic Regression**: Baseline linear model
    - Hyperparams: C (regularization), penalty (L1/L2)
  - **Random Forest**: Ensemble tree-based model
    - Hyperparams: n_estimators, max_depth, min_samples_split
    - Feature importance analysis
  - **XGBoost**: Gradient boosting
    - Hyperparams: learning_rate, max_depth, subsample
    - Best performance in most cases

**Model Deployment**:

  - Best model saved to MLflow registry
  - Version tracking and comparison
  - Production model loading with fallback
  - Confidence scores via probability estimates

- **Risk Score Calculation**
  - **Output**: 0-1 continuous score
  - **Classification**: Low (<0.33), Medium (0.33-0.66), High (>0.66)
  - **Confidence**: Maximum class probability
  - **Explainability**: Feature importance and SHAP values

- **Alternative ML System** (`MLRiskScorer`)
  - Multi-algorithm testing (RF, XGBoost, LightGBM, CatBoost)
  - SMOTE for class imbalance handling
  - Feature importance via permutation
  - Model persistence with joblib

- **Anomaly Detection** (`AnomalyDetector`)
  - Isolation Forest for outlier detection
  - Local Outlier Factor (LOF)
  - One-Class SVM
  - HBOS (Histogram-Based Outlier Score)
  - KNN (Distance-based)
  - AutoEncoder (Deep Learning-based)
  - Contamination rate: 10%
  - Anomaly scores: 0-1 scale

- **MLflow Integration**
  - Experiment tracking
  - Model versioning and registry
  - Performance metrics logging
  - A/B testing framework
  - Model comparison dashboard

### 6. Key Features & Capabilities (4-5 pages)

**A. Risk Dashboard**

- Real-time protocol monitoring (20 protocols)
- Risk heatmap visualization
- Interactive protocol selection
- Historical risk trends (7-30 day charts)
- System health indicators

**B. Advanced Analytics**

- Risk metrics cards (high/medium/low counts)
- TVL aggregation across protocols
- Risk level distribution
- Protocol comparison views
- Trend analysis with Recharts

**C. Portfolio Analyzer**

- Custom portfolio creation
- Aggregated risk assessment
- Diversification analysis
- Risk-weighted portfolio scoring

**D. AI Assistant (RAG-Powered)**

- **LLM**: Ollama with TinyLlama model
- **Embeddings**: all-minilm for efficiency
- **Vector Store**: FAISS with 500-token chunks
- **Knowledge Base**: Protocol data, risk metrics, DeFi concepts
- **Guardrails**: Scope-limited responses, query validation
- **Features**:
  - Natural language queries about protocols
  - Risk explanation and analysis
  - DeFi domain knowledge
  - Context-aware responses
  - Source attribution

**E. Email Alert System**

- Customizable risk thresholds
- Email subscription management
- High/medium risk notifications
- SMTP integration (Gmail)
- Unsubscribe functionality

**F. Real-Time Data Updates**

- Automated data collection (15-minute intervals)
- Risk recalculation (30-minute intervals)
- WebSocket-ready architecture
- Query caching (30-second intervals)

### 7. GCP Production Deployment (5-6 pages)

**Infrastructure Setup**:

- **GCP VM**: Debian-based compute instance
- **Domain**: safefi.live, api.safefi.live
- **SSL/TLS**: Let's Encrypt certificates
- **Reverse Proxy**: Nginx (version 1.22.1)

**Nginx Configuration**:

- Frontend serving from Google Cloud Storage
- API reverse proxy to localhost:8000
- CORS handling for cross-origin requests
- Extended timeouts for LLM requests (600s)
- SSL termination and security headers

**Backend Services** (systemd):

- **defi-backend.service**: FastAPI application
  - Port: 8000
  - Workers: Single process (Uvicorn)
  - Restart policy: Always with 10s delay
  - Dependencies: PostgreSQL, Ollama

- **ollama.service**: LLM inference server
  - Port: 11434
  - Model: TinyLlama (1.1GB)
  - Embedding model: all-minilm
  - Host: 127.0.0.1

- **postgresql.service**: Database server
  - Database: defi_risk_assessment
  - User: defi_user
  - Connection pooling enabled

**Environment Configuration**:

```env
DATABASE_URL=postgresql+psycopg2://defi_user:***@localhost:5432/defi_risk_assessment
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama
CORS_ORIGINS=https://safefi.live
ENVIRONMENT=production
```

**Deployment Workflow**:

1. Database initialization
2. Protocol seeding (20 real protocols)
3. Live data collection
4. Risk score calculation
5. Vector store initialization (10-15 minutes)
6. Service startup and health checks

**Monitoring & Logging**:

- Systemd journald for service logs
- MLflow tracking UI (port 5000)
- Structured JSON logging in production
- Health check endpoints (/health, /llm/health)

**Security**:

- HTTPS-only communication
- HSTS headers (max-age: 1 year)
- X-Frame-Options: DENY
- Content Security Policy headers
- API key management via environment variables
- SQL injection prevention (parameterized queries)
- CORS whitelisting

**Performance Optimization**:

- Database indexing (protocol_id, timestamp)
- Query result caching
- Async I/O operations
- Connection pooling
- CDN for static assets (GCS)
- Compression for API responses

### 8. DeFi Domain Knowledge (3-4 pages)

**Core DeFi Concepts**:

- **Total Value Locked (TVL)**: Total crypto assets deposited in protocol
  - Primary indicator of protocol size and trust
  - Measured in USD equivalent
  - Higher TVL typically indicates more established protocols

- **Liquidity**: Ability to buy/sell assets without significant price impact
  - Critical for DEXs and lending protocols
  - Measured by trading volume and depth
  - Low liquidity increases slippage risk

- **Volatility**: Price fluctuation magnitude
  - Higher volatility = higher risk
  - Measured by standard deviation
  - Affects impermanent loss and liquidation risk

- **Market Capitalization**: Total value of circulating tokens
  - Indicator of protocol scale
  - More stable for large-cap protocols
  - Affects voting power in governance

**Protocol Categories**:

- **DEX (Decentralized Exchanges)**:
  - Automated Market Makers (AMMs)
  - Liquidity pools and LP tokens
  - Trading fees and slippage
  - Examples: Uniswap, Curve, SushiSwap

- **Lending Protocols**:
  - Over-collateralized loans
  - Interest rates (supply/borrow APY)
  - Liquidation mechanisms
  - Examples: Aave, Compound, MakerDAO

- **Yield Aggregators**:
  - Automated yield farming
  - Strategy optimization
  - Auto-compounding
  - Examples: Yearn Finance, Convex

- **Liquid Staking**:
  - Staking with liquidity
  - Derivative tokens (stETH, rETH)
  - Validator risks
  - Examples: Lido, Rocket Pool

- **Derivatives**:
  - Perpetual futures
  - Options and synthetic assets
  - Leverage and margin trading
  - Examples: dYdX, GMX

**Risk Factors**:

- **Smart Contract Risk**: Code vulnerabilities and exploits
- **Liquidity Risk**: Inability to exit positions
- **Oracle Risk**: Price feed manipulation
- **Regulatory Risk**: Legal uncertainty
- **Market Risk**: Price volatility and cascading liquidations
- **Counterparty Risk**: Protocol insolvency

### 9. API Reference (2-3 pages)

**Base URL**: `https://api.safefi.live`

**Key Endpoints**:

- `GET /protocols` - List all monitored protocols
- `GET /protocols/{id}/metrics` - Protocol time-series data
- `GET /ml/risk/protocols/{id}/risk-details` - Detailed risk analysis
- `POST /ml/risk/calculate-batch` - Recalculate all risk scores
- `POST /models/train` - Train ML models
- `GET /models/performance` - Model metrics
- `POST /llm/query` - AI assistant queries
- `GET /llm/health` - LLM service status
- `GET /health` - System health check

**Response Format**:

```json
{
  "data": { ... },
  "meta": { ... }
}
```

### 10. Operational Guide (2-3 pages)

**Daily Operations**:

- Monitor system health dashboard
- Review risk alerts
- Check data collection status
- Verify ML model performance

**Maintenance Tasks**:

- Weekly: Review and update thresholds
- Monthly: Retrain ML models with new data
- Quarterly: Add new protocols, update dependencies

**Troubleshooting**:

- LLM service unavailable: Check Ollama service status
- Data collection failures: Verify API keys and rate limits
- Database connection issues: Check PostgreSQL service
- High risk scores: Validate with external sources

**Backup & Recovery**:

- Database: Daily automated backups
- Models: Versioned in MLflow registry
- Configuration: Version controlled in Git

### 11. Future Roadmap (1 page)

- Multi-chain expansion
- Advanced risk models (LSTMs for time-series)
- Real-time WebSocket updates
- Mobile application
- DeFi protocol audits integration
- Social sentiment analysis
- Governance proposal tracking

## Implementation Notes

- Document should be 25-30 pages
- Include code snippets where relevant
- Add ASCII diagrams for architecture
- Use tables for feature comparisons
- Include actual metrics from production
- Reference specific file paths in codebase
- Add troubleshooting section for common issues