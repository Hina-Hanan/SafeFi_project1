from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class ORMConfig(BaseModel):
    model_config = dict(from_attributes=True)


class ProtocolOut(ORMConfig):
    id: str
    name: str
    symbol: Optional[str] = None
    contract_address: Optional[str] = None
    category: str
    chain: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProtocolWithRiskOut(ProtocolOut):
    latest_risk_score: Optional[float] = None
    latest_risk_level: Optional[str] = None
    latest_model_version: Optional[str] = None
    latest_timestamp: Optional[datetime] = None


class ProtocolMetricOut(ORMConfig):
    id: str
    protocol_id: str
    tvl: Optional[float] = None
    volume_24h: Optional[float] = None
    price: Optional[float] = None
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class RiskScoreOut(ORMConfig):
    id: str
    protocol_id: str
    risk_level: str
    risk_score: float
    volatility_score: Optional[float] = None
    liquidity_score: Optional[float] = None
    model_version: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime


class AlertCreate(BaseModel):
    user_id: str
    protocol_id: str
    risk_threshold: float = Field(ge=0.0, le=1.0)
    is_active: bool = True


class AlertOut(ORMConfig):
    id: str
    user_id: str
    protocol_id: str
    risk_threshold: float
    is_active: bool
    last_triggered: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


