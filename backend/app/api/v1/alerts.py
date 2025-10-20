from fastapi import APIRouter, Depends, status
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Alert, Protocol, User
from app.api.v1.schemas import AlertCreate, AlertOut


router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    protocol = db.query(Protocol).get(payload.protocol_id)
    user = db.query(User).get(payload.user_id)
    if not protocol:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocol not found")
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    alert = Alert(
        user_id=payload.user_id,
        protocol_id=payload.protocol_id,
        risk_threshold=payload.risk_threshold,
        is_active=payload.is_active,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


