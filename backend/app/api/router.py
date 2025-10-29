from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.risk import router as risk_router
from app.api.v1.protocols import router as protocols_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.alerts import router as alerts_router
from app.api.v1.data import router as data_router
from app.api.v1.email_alerts import router as email_alerts_router
from app.api.v1.monitoring import router as monitoring_router
from app.api.v1.ml import (
    router as ml_model_router,
    risk_router as ml_risk_router,
    anomaly_router,
    feature_router
)

# Optional LLM assistant router (requires RAG dependencies)
try:
    from app.api.v1.llm_assistant import router as llm_assistant_router
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(risk_router)
api_router.include_router(protocols_router)
api_router.include_router(metrics_router)
api_router.include_router(alerts_router)
api_router.include_router(data_router)
api_router.include_router(email_alerts_router)  # Email alert system
api_router.include_router(monitoring_router)  # Real-time monitoring
if LLM_AVAILABLE:
    api_router.include_router(llm_assistant_router, prefix="/llm", tags=["llm-assistant"])  # RAG-powered LLM Assistant
api_router.include_router(ml_model_router)
api_router.include_router(ml_risk_router)
api_router.include_router(anomaly_router)  # New anomaly detection endpoints
api_router.include_router(feature_router)  # New feature importance endpoints



