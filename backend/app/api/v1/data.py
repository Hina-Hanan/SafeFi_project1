from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.data_collector import DataCollectorService


class DataCollectRequest(BaseModel):
    source: str = Field(description="coingecko or defillama")
    protocol_ids: list[str] | None = None


class DataCollectResponse(BaseModel):
    started: bool
    source: str
    protocols_processed: int


router = APIRouter(prefix="/data", tags=["data"])


@router.post("/collect", response_model=DataCollectResponse)
async def trigger_data_collection(
    payload: DataCollectRequest, db: Session = Depends(get_db)
) -> DataCollectResponse:
    service = DataCollectorService(db=db)
    try:
        processed = await service.collect(source=payload.source, protocol_ids=payload.protocol_ids)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    return DataCollectResponse(started=True, source=payload.source, protocols_processed=processed)


