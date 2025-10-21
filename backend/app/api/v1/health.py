import os
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Protocol, ProtocolMetric, RiskScore

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    """Health check endpoint with comprehensive system status."""
    import logging
    logger = logging.getLogger(__name__)
    
    database_connected = False
    total_protocols = 0
    total_metrics = 0
    total_risk_scores = 0
    total_tvl_usd = 0.0
    
    try:
        # Test database connection with a simple query
        from sqlalchemy import select, func
        
        # Try to get counts
        total_protocols = db.scalar(select(func.count()).select_from(Protocol)) or 0
        total_metrics = db.scalar(select(func.count()).select_from(ProtocolMetric)) or 0
        total_risk_scores = db.scalar(select(func.count()).select_from(RiskScore)) or 0
        
        # Calculate total TVL from latest metrics for each protocol
        if total_protocols > 0:
            # Simple approach: get latest TVL for each protocol
            protocol_ids = [p.id for p in db.query(Protocol).all()]
            total_tvl_usd = 0.0
            
            for protocol_id in protocol_ids:
                latest_metric = (
                    db.query(ProtocolMetric)
                    .filter(ProtocolMetric.protocol_id == protocol_id)
                    .filter(ProtocolMetric.tvl.isnot(None))
                    .order_by(ProtocolMetric.timestamp.desc())
                    .first()
                )
                if latest_metric and latest_metric.tvl:
                    total_tvl_usd += float(latest_metric.tvl)
        
        # If we got here, database is connected
        database_connected = True
        logger.info(f"Health check: DB connected, {total_protocols} protocols, ${total_tvl_usd:,.0f} total TVL")
        
    except Exception as e:
        # Log the error details
        logger.error(f"Database health check failed: {type(e).__name__}: {e}", exc_info=True)
        database_connected = False
    
    # Check if MLflow is accessible (check if mlruns directory exists)
    mlflow_connected = os.path.exists("mlruns") or os.path.exists("../mlruns")
    
    return {
        "status": "ok",
        "database_connected": database_connected,
        "mlflow_connected": mlflow_connected,
        "timestamp": datetime.utcnow().isoformat(),
        "total_protocols": total_protocols,
        "total_metrics": total_metrics,
        "total_risk_scores": total_risk_scores,
        "total_tvl_usd": total_tvl_usd,
    }


@router.get("/metrics")
def get_system_metrics(db: Session = Depends(get_db)) -> dict:
    """Get system-wide metrics for dashboard cards."""
    try:
        from sqlalchemy import select, func
        total_protocols = db.scalar(select(func.count()).select_from(Protocol))
        total_metrics = db.scalar(select(func.count()).select_from(ProtocolMetric))
        total_risk_scores = db.scalar(select(func.count()).select_from(RiskScore))
        
        # Calculate total TVL from latest metrics for each protocol
        total_tvl_usd = 0.0
        if total_protocols and total_protocols > 0:
            # Simple approach: get latest TVL for each protocol
            protocol_ids = [p.id for p in db.query(Protocol).all()]
            
            for protocol_id in protocol_ids:
                latest_metric = (
                    db.query(ProtocolMetric)
                    .filter(ProtocolMetric.protocol_id == protocol_id)
                    .filter(ProtocolMetric.tvl.isnot(None))
                    .order_by(ProtocolMetric.timestamp.desc())
                    .first()
                )
                if latest_metric and latest_metric.tvl:
                    total_tvl_usd += float(latest_metric.tvl)
        
        return {
            "total_protocols": total_protocols or 0,
            "total_metrics": total_metrics or 0,
            "total_risk_scores": total_risk_scores or 0,
            "total_tvl_usd": total_tvl_usd,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"System metrics query failed: {e}")
        return {
            "total_protocols": 0,
            "total_metrics": 0,
            "total_risk_scores": 0,
            "total_tvl_usd": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }



