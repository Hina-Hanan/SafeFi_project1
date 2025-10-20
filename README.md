Safefi - DeFi Risk Assessment Platform

## Overview
Safefi is a professional DeFi risk assessment platform that provides real-time monitoring, ML-powered risk scoring, and institutional-grade analytics.

## ✨ NEW: RAG-Powered LLM Assistant 🤖

**Ask questions about your protocols using natural language!**

```bash
# Example: "What are the high-risk protocols?"
curl -X POST http://YOUR_SERVER:8000/api/v1/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the high-risk protocols?"}'
```

**Features:**
- 🆓 **100% Free** - Uses Ollama (TinyLlama, Mistral, Llama 3)
- 🔍 **RAG-Powered** - Retrieves context from your database
- 🚀 **Streaming** - Real-time token-by-token responses
- ☁️ **Cloud Ready** - Deploy to GCP free tier
- 📊 **Context-Aware** - Answers based on real risk scores & metrics

**🎯 Recommended Workflow:**

1. **Test Locally First** (30 min) → `QUICK_LOCAL_TEST.md` or `LOCAL_TESTING_GUIDE.md`
2. **Deploy to Production** (2 hours) → `START_HERE.md`

```bash
# Quick local test (if you have PostgreSQL & Node.js):
cd backend && python -m uvicorn app.main:app --reload
cd frontend && npm run dev
# Open: http://localhost:5173

# Then deploy to GCP + Vercel (see START_HERE.md)
```

📚 **Documentation:**

**Getting Started:**
- ⭐ **START HERE**: `START_HERE.md` - Production deployment guide
- 🧪 **Test Locally First**: `LOCAL_TESTING_GUIDE.md` - Run locally before deploying
- ⚡ **Quick Local Test**: `QUICK_LOCAL_TEST.md` - 5-minute local verification
- 🔄 **Complete Workflow**: `TESTING_WORKFLOW.md` - Local → Production flow

**Detailed Guides:**
- ✅ **Checklist**: `LLM_SETUP_CHECKLIST.md` - Track your progress
- 📖 **Backend Details**: `GCP_TINYLLAMA_SETUP.md` - GCP setup instructions
- 🎨 **Frontend Details**: `FRONTEND_DEPLOYMENT.md` - Vercel deployment
- 📝 **API Examples**: `markdowns/RAG_API_EXAMPLES.md` - Code samples
- 🔧 **Advanced**: `markdowns/RAG_LLM_INTEGRATION.md` - Deep dive  

---

## Tech Stack
- Backend: FastAPI, SQLAlchemy, PostgreSQL, MLflow
- Frontend: React 18, TypeScript, Material-UI (MUI), React Query
- ML Pipeline: scikit-learn, pandas, numpy, MLflow
- **LLM/RAG: Ollama, LangChain, FAISS, sentence-transformers**
- Deployment: AWS Lambda, ECS, RDS, Amplify
- Data Sources: CoinGecko, DeFiLlama

Monorepo Structure
```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── risk.py
│   │   │   │   └── health.py
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── logging_config.py
│   │   ├── services/
│   │   │   ├── risk_scoring.py
│   │   │   ├── data_providers/
│   │   │   │   ├── coingecko_client.py
│   │   │   │   └── defillama_client.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── models.py
│   │   │   └── session.py
│   │   ├── ml/
│   │   │   ├── inference.py
│   │   │   └>> training/
│   │   │       └── train.py
│   │   ├── main.py
│   │   └── __init__.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   └── risk.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   └── RiskScoreCard.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   └── Protocol.tsx
│   │   ├── hooks/
│   │   │   └── useRiskScore.ts
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── index.html
│   ├── tsconfig.json
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── ml/
│   ├── notebooks/
│   ├── pipelines/
│   │   ├── data_prep.py
│   │   ├── features.py
│   │   └── train.py
│   ├── requirements.txt
│   └── mlflow/
│       └── tracking_uri.README
├── infra/
│   ├── aws/
│   │   ├── lambda/
│   │   │   └── placeholder.md
│   │   ├── ecs/
│   │   │   └── placeholder.md
│   │   ├── rds/
│   │   │   └── placeholder.md
│   │   └── amplify/
│   │       └── placeholder.md
├── docker-compose.yml
└── .gitignore
```

Getting Started (Dev)
1. Install Docker and Docker Compose
2. Copy `.env.example` to `.env`
3. Start services: `docker compose up -d`
4. Backend: uvicorn at `http://localhost:8000` (once implemented)
5. Frontend: Vite dev server at `http://localhost:5173`

License
Proprietary – All rights reserved.



