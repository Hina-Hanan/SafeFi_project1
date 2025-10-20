from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.api.schemas import (
    DataCollectRequest,
    DataCollectResponse,
    ListResponse,
    Meta,
    ObjectResponse,
    Protocol as ProtocolSchema,
    ProtocolMetric as ProtocolMetricSchema,
    ProtocolRisk as ProtocolRiskSchema,
    ProtocolWithRisk,
)
from app.database.connection import get_db
from app.database.models import Protocol, ProtocolMetric, RiskScore
from app.services.data_collector import DataCollectorService


logger = logging.getLogger("app.api.routes")
router = APIRouter()


@router.get("/protocols", response_model=ListResponse, tags=["protocols"])
async def list_protocols(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> ListResponse:
    try:
        total = db.scalar(select(Protocol).count())  # type: ignore[attr-defined]
    except Exception:
        # SQLAlchemy 2.0 safe count fallback
        total = db.scalar(select(db.query(Protocol).count().subquery()))  # type: ignore[attr-defined]

    protocols = db.execute(
        select(Protocol).order_by(Protocol.name).limit(limit).offset(offset)
    ).scalars().all()

    # Fetch latest risk per protocol
    results: list[ProtocolWithRisk] = []
    for p in protocols:
        risk = db.execute(
            select(RiskScore).where(RiskScore.protocol_id == p.id).order_by(desc(RiskScore.timestamp)).limit(1)
        ).scalars().first()
        results.append(
            ProtocolWithRisk(
                protocol=ProtocolSchema(
                    id=p.id,
                    name=p.name,
                    symbol=p.symbol,
                    contract_address=p.contract_address,
                    category=p.category,
                    chain=p.chain,
                    is_active=p.is_active,
                ),
                current_risk=(
                    ProtocolRiskSchema(
                        protocol_id=risk.protocol_id,
                        risk_level=risk.risk_level,
                        risk_score=risk.risk_score,
                        volatility_score=risk.volatility_score,
                        liquidity_score=risk.liquidity_score,
                        model_version=risk.model_version,
                        timestamp=risk.timestamp,
                    )
                    if risk
                    else None
                ),
            )
        )

    return ListResponse(data=results, meta=Meta(page=offset // limit + 1, limit=limit, total=total))


@router.get("/protocols/{protocol_id}/risk", response_model=ObjectResponse, tags=["protocols"])
async def get_protocol_risk(protocol_id: str, db: Session = Depends(get_db)) -> ObjectResponse:
    protocol = db.get(Protocol, protocol_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")

    risks = db.execute(
        select(RiskScore).where(RiskScore.protocol_id == protocol_id).order_by(desc(RiskScore.timestamp))
    ).scalars().all()

    data = [
        ProtocolRiskSchema(
            protocol_id=r.protocol_id,
            risk_level=r.risk_level,
            risk_score=r.risk_score,
            volatility_score=r.volatility_score,
            liquidity_score=r.liquidity_score,
            model_version=r.model_version,
            timestamp=r.timestamp,
        )
        for r in risks
    ]
    return ObjectResponse(data=data, meta=Meta())


@router.get("/protocols/{protocol_id}/metrics", response_model=ListResponse, tags=["metrics"])
async def get_protocol_metrics(
    protocol_id: str,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> ListResponse:
    protocol = db.get(Protocol, protocol_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")

    metrics = (
        db.execute(
            select(ProtocolMetric)
            .where(ProtocolMetric.protocol_id == protocol_id)
            .order_by(desc(ProtocolMetric.timestamp))
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    data = [
        ProtocolMetricSchema(
            protocol_id=m.protocol_id,
            tvl=float(m.tvl) if m.tvl is not None else None,
            volume_24h=float(m.volume_24h) if m.volume_24h is not None else None,
            price=float(m.price) if m.price is not None else None,
            market_cap=float(m.market_cap) if m.market_cap is not None else None,
            price_change_24h=m.price_change_24h,
            timestamp=m.timestamp,
        )
        for m in metrics
    ]

    # Best-effort total estimate (optional for large tables)
    total: int | None = None
    try:
        total = db.query(ProtocolMetric).filter_by(protocol_id=protocol_id).count()  # type: ignore[attr-defined]
    except Exception:
        pass

    return ListResponse(data=data, meta=Meta(page=offset // max(1, limit) + 1, limit=limit, total=total))


@router.post("/data/collect", response_model=ObjectResponse, tags=["data"])
async def trigger_data_collection(
    payload: DataCollectRequest,
    db: Session = Depends(get_db),
) -> ObjectResponse:
    service = DataCollectorService(db=db)
    try:
        processed = await service.collect(source=payload.source, protocol_ids=payload.protocol_ids)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:  # pragma: no cover - unexpected
        logger.exception("Data collection failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Collection failed")

    return ObjectResponse(
        data=DataCollectResponse(started=True, source=payload.source, protocols_processed=processed).dict(),
        meta=Meta(),
    )


api_router = APIRouter()
api_router.include_router(router)


