from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Protocol, RiskScore, ProtocolMetric
from app.api.v1.schemas import ProtocolOut, ProtocolWithRiskOut


router = APIRouter(prefix="/protocols", tags=["protocols"])


@router.get("")
def list_protocols(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    active: Optional[bool] = Query(None),
    chain: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    """List protocols with latest risk scores and metrics in frontend-compatible format."""
    q = db.query(Protocol)
    if active is not None:
        q = q.filter(Protocol.is_active == active)
    if chain:
        q = q.filter(Protocol.chain == chain)
    if category:
        q = q.filter(Protocol.category == category)
    protocols = q.order_by(Protocol.name.asc()).offset(offset).limit(limit).all()

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

    # Build response in frontend-compatible format
    result = []
    for p in protocols:
        rs = latest_scores.get(p.id)
        metric = latest_metrics.get(p.id)
        
        protocol_data = {
            "id": p.id,
            "name": p.name,
            "symbol": p.symbol,
            "contract_address": p.contract_address,
            "category": p.category,
            "chain": p.chain,
            "is_active": p.is_active,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        }
        
        # Add nested latest_risk object
        if rs:
            protocol_data["latest_risk"] = {
                "risk_score": float(rs.risk_score),
                "risk_level": rs.risk_level,
                "volatility_score": float(rs.volatility_score) if rs.volatility_score else None,
                "liquidity_score": float(rs.liquidity_score) if rs.liquidity_score else None,
                "model_version": rs.model_version,
                "timestamp": rs.timestamp.isoformat() if rs.timestamp else None,
            }
        else:
            protocol_data["latest_risk"] = None
        
        # Add nested latest_metrics object  
        if metric:
            protocol_data["latest_metrics"] = {
                "tvl_usd": float(metric.tvl) if metric.tvl else None,
                "volume_24h_usd": float(metric.volume_24h) if metric.volume_24h else None,
                "price": float(metric.price) if metric.price else None,
                "market_cap": float(metric.market_cap) if metric.market_cap else None,
                "price_change_24h": float(metric.price_change_24h) if metric.price_change_24h else None,
                "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
            }
        else:
            protocol_data["latest_metrics"] = None
            
        result.append(protocol_data)
    
    return result


@router.get("/{protocol_id}", response_model=ProtocolOut)
def get_protocol(protocol_id: str, db: Session = Depends(get_db)):
    protocol = db.query(Protocol).get(protocol_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")
    return protocol


