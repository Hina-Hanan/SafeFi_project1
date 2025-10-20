from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Protocol, ProtocolMetric
from app.api.v1.schemas import ProtocolMetricOut


router = APIRouter(prefix="/protocols", tags=["metrics"])


@router.get("/{protocol_id}/metrics", response_model=List[ProtocolMetricOut])
def get_protocol_metrics(
    protocol_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    protocol = db.query(Protocol).get(protocol_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")
    rows = (
        db.query(ProtocolMetric)
        .filter(ProtocolMetric.protocol_id == protocol_id)
        .order_by(ProtocolMetric.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return rows


