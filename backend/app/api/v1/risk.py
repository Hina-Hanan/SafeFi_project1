from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Protocol, RiskScore
from app.api.v1.schemas import RiskScoreOut


router = APIRouter(prefix="/risk", tags=["risk"]) 


@router.get("/score", response_model=RiskScoreOut)
def get_risk_score(
    protocol_id: str = Query(..., description="Protocol ID"),
    db: Session = Depends(get_db),
):
    protocol = db.query(Protocol).get(protocol_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")
    row = (
        db.query(RiskScore)
        .filter(RiskScore.protocol_id == protocol_id)
        .order_by(RiskScore.timestamp.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk score not found")
    return row


@router.get("/protocols/{protocol_id}/history")
def get_protocol_risk_history(
    protocol_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records"),
    db: Session = Depends(get_db),
):
    """Get risk score history for a protocol."""
    # Verify protocol exists
    protocol = db.query(Protocol).filter_by(id=protocol_id).first()
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol not found: {protocol_id}"
        )
    
    # Calculate cutoff date
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Query risk scores
    risk_scores = (
        db.query(RiskScore)
        .filter(
            RiskScore.protocol_id == protocol_id,
            RiskScore.timestamp >= cutoff_date
        )
        .order_by(RiskScore.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    # Convert to simple dict list for frontend
    return [
        {
            "id": rs.id,
            "protocol_id": rs.protocol_id,
            "risk_score": float(rs.risk_score),
            "risk_level": rs.risk_level,
            "model_version": rs.model_version,
            "timestamp": rs.timestamp.isoformat(),
            "volatility_score": float(rs.volatility_score) if rs.volatility_score else None,
            "liquidity_score": float(rs.liquidity_score) if rs.liquidity_score else None,
        }
        for rs in risk_scores
    ]




