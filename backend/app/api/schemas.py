from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Meta(BaseModel):
    page: Optional[int] = Field(default=None)
    limit: Optional[int] = Field(default=None)
    total: Optional[int] = Field(default=None)
    error: Optional[str] = Field(default=None)


class Protocol(BaseModel):
    id: str
    name: str
    symbol: Optional[str] = None
    contract_address: Optional[str] = None
    category: str
    chain: str
    is_active: bool


class ProtocolRisk(BaseModel):
    protocol_id: str
    risk_level: str
    risk_score: float
    volatility_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    model_version: str
    timestamp: datetime


class ProtocolWithRisk(BaseModel):
    protocol: Protocol
    current_risk: Optional[ProtocolRisk] = None


class ProtocolMetric(BaseModel):
    protocol_id: str
    tvl: Optional[float] = None
    volume_24h: Optional[float] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime


class DataCollectRequest(BaseModel):
    source: str = Field(description="data source: coingecko or defillama")
    protocol_ids: list[str] | None = None


class DataCollectResponse(BaseModel):
    started: bool
    source: str
    protocols_processed: int


class ListResponse(BaseModel):
    data: list[Any]
    meta: Meta


class ObjectResponse(BaseModel):
    data: Any | None
    meta: Meta


