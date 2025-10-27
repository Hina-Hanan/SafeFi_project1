from datetime import datetime
from uuid import uuid4
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class ProtocolCategoryEnum(str, PyEnum):  # type: ignore[misc]
    LENDING = "lending"
    DEX = "dex"
    DERIVATIVES = "derivatives"
    YIELD = "yield"
    STAKING = "staking"
    BRIDGE = "bridge"
    OTHER = "other"


class RiskLevelEnum(str, PyEnum):  # type: ignore[misc]
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


def default_uuid() -> str:
    return str(uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Protocol(Base, TimestampMixin):
    __tablename__ = "protocols"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    symbol: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    contract_address: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[str] = mapped_column(SQLEnum(ProtocolCategoryEnum, name="protocol_category"), nullable=False, default=ProtocolCategoryEnum.OTHER)
    chain: Mapped[str] = mapped_column(String(100), nullable=False, default="ethereum")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    metrics: Mapped[list["ProtocolMetric"]] = relationship("ProtocolMetric", back_populates="protocol", cascade="all, delete-orphan")
    risk_scores: Mapped[list["RiskScore"]] = relationship("RiskScore", back_populates="protocol", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_protocols_name_chain", "name", "chain", unique=True),
    )


class ProtocolMetric(Base, TimestampMixin):
    __tablename__ = "protocol_metrics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
    protocol_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("protocols.id", ondelete="CASCADE"), index=True)
    tvl: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    volume_24h: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(20, 8), nullable=True)
    market_cap: Mapped[float | None] = mapped_column(Numeric(20, 2), nullable=True)
    price_change_24h: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    protocol: Mapped["Protocol"] = relationship("Protocol", back_populates="metrics")

    __table_args__ = (
        Index("ix_protocol_metrics_protocol_time", "protocol_id", "timestamp"),
    )


class RiskScore(Base, TimestampMixin):
    __tablename__ = "risk_scores"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
    protocol_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("protocols.id", ondelete="CASCADE"), index=True)
    risk_level: Mapped[str] = mapped_column(SQLEnum(RiskLevelEnum, name="risk_level"), nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    volatility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    liquidity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    protocol: Mapped["Protocol"] = relationship("Protocol", back_populates="risk_scores")

    __table_args__ = (
        Index("ix_risk_scores_protocol_time", "protocol_id", "timestamp"),
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    encrypted_password: Mapped[str] = mapped_column(String(255), nullable=False)
    subscription_tier: Mapped[str] = mapped_column(String(50), nullable=False, default="free")

    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="user", cascade="all, delete-orphan")


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=default_uuid, index=True)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    protocol_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("protocols.id", ondelete="CASCADE"), index=True)
    risk_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_triggered: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="alerts")
    protocol: Mapped["Protocol"] = relationship("Protocol")


class EmailSubscriber(Base, TimestampMixin):
    """Email subscribers for risk alert notifications."""
    __tablename__ = "email_subscribers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=default_uuid, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Alert preferences
    high_risk_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=70.0)
    medium_risk_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=40.0)
    notify_on_high: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_on_medium: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Subscription metadata
    verification_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unsubscribe_token: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_alert_sent: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("ix_email_subscribers_email", "email"),
        Index("ix_email_subscribers_active", "is_active"),
    )


