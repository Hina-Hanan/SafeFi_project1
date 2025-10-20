"""
Collect protocol data and write realistic, varied risk scores.

Note: This script generates simulated-but-realistic metrics and risk values
to exercise the dashboard end-to-end when live API collection is rate-limited.
"""
import logging
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolMetric, RiskScore
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.collect_data")


# Realistic protocol profiles with different risk characteristics
PROTOCOL_PROFILES = {
    "Uniswap": {"base_tvl": 2_900_000_000, "volatility": 0.85, "liquidity": 0.95, "volume_ratio": 0.8, "price_volatility": 0.15},
    "Aave": {"base_tvl": 44_617_000_000, "volatility": 0.35, "liquidity": 0.90, "volume_ratio": 0.4, "price_volatility": 0.08},
    "Curve": {"base_tvl": 2_200_000_000, "volatility": 0.25, "liquidity": 0.95, "volume_ratio": 0.6, "price_volatility": 0.05},
    "Compound": {"base_tvl": 2_400_000_000, "volatility": 0.40, "liquidity": 0.85, "volume_ratio": 0.5, "price_volatility": 0.10},
    "MakerDAO": {"base_tvl": 5_000_000, "volatility": 0.20, "liquidity": 0.98, "volume_ratio": 0.3, "price_volatility": 0.03},
    "SushiSwap": {"base_tvl": 167_700_000, "volatility": 0.75, "liquidity": 0.70, "volume_ratio": 0.7, "price_volatility": 0.18},
    "1inch": {"base_tvl": 6_000_000, "volatility": 0.60, "liquidity": 0.75, "volume_ratio": 0.65, "price_volatility": 0.12},
    "Balancer": {"base_tvl": 555_000_000, "volatility": 0.50, "liquidity": 0.80, "volume_ratio": 0.55, "price_volatility": 0.11},
    "Yearn Finance": {"base_tvl": 573_600_000, "volatility": 0.55, "liquidity": 0.75, "volume_ratio": 0.45, "price_volatility": 0.13},
    "Synthetix": {"base_tvl": 100_000_000, "volatility": 0.80, "liquidity": 0.65, "volume_ratio": 0.60, "price_volatility": 0.20},
    "PancakeSwap": {"base_tvl": 2_000_000_000, "volatility": 0.70, "liquidity": 0.85, "volume_ratio": 0.75, "price_volatility": 0.16},
    "Lido": {"base_tvl": 38_200_000_000, "volatility": 0.30, "liquidity": 0.95, "volume_ratio": 0.35, "price_volatility": 0.06},
}


def generate_metrics_for_protocol(protocol_name: str, profile: dict) -> dict:
    tvl_variance = random.uniform(0.95, 1.05)
    tvl_usd = profile["base_tvl"] * tvl_variance
    volume_24h = tvl_usd * profile["volume_ratio"] * random.uniform(0.8, 1.2)
    price_change_24h = random.gauss(0, profile["price_volatility"] * 100)
    base_price = random.uniform(1, 100)
    price = base_price * (1 + price_change_24h / 100)
    market_cap = tvl_usd * random.uniform(0.8, 1.5)
    return {"tvl_usd": tvl_usd, "volume_24h_usd": volume_24h, "price": price, "market_cap": market_cap, "price_change_24h": price_change_24h}


def calculate_risk_score(profile: dict, metrics: dict) -> tuple:
    volatility_risk = profile["volatility"]
    liquidity_risk = 1 - profile["liquidity"]
    price_vol_risk = min(abs(metrics["price_change_24h"]) / 20, 1)
    volume_risk = 1 - min(profile["volume_ratio"], 1)
    risk_score = volatility_risk * 0.40 + liquidity_risk * 0.30 + price_vol_risk * 0.20 + volume_risk * 0.10
    risk_score = min(max(risk_score * random.uniform(0.95, 1.05), 0), 1)
    if risk_score >= 0.70:
        risk_level = "high"
    elif risk_score >= 0.40:
        risk_level = "medium"
    else:
        risk_level = "low"
    return risk_score, risk_level, volatility_risk, liquidity_risk


def main():
    logger.info("=" * 60)
    logger.info("🎲 Collecting protocol data (simulated realistic)...")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)

    with managed_session() as db:
        protocols = db.execute(select(Protocol).where(Protocol.is_active == True)).scalars().all()
        if not protocols:
            logger.error("❌ No protocols found in database!")
            return

        logger.info(f"📊 Found {len(protocols)} protocols")
        metrics_written = 0
        risks_written = 0

        # ensure newest timestamp
        try:
            from sqlalchemy import func as _func
            latest_existing = db.execute(select(_func.max(RiskScore.timestamp))).scalar()
        except Exception:
            latest_existing = None
        base_now = datetime.utcnow()
        try:
            latest_ts = latest_existing.replace(tzinfo=None) if latest_existing else None
        except Exception:
            latest_ts = latest_existing
        timestamp = (latest_ts + timedelta(seconds=5)) if (latest_ts and latest_ts >= base_now) else base_now

        for protocol in protocols:
            profile = PROTOCOL_PROFILES.get(protocol.name, {"base_tvl": 100_000_000, "volatility": 0.45, "liquidity": 0.75, "volume_ratio": 0.50, "price_volatility": 0.10})
            m = generate_metrics_for_protocol(protocol.name, profile)
            db.add(ProtocolMetric(protocol_id=protocol.id, tvl=Decimal(str(m["tvl_usd"])), volume_24h=Decimal(str(m["volume_24h_usd"])), price=Decimal(str(m["price"])), market_cap=Decimal(str(m["market_cap"])), price_change_24h=Decimal(str(m["price_change_24h"])), timestamp=timestamp))
            metrics_written += 1
            score, level, vol_risk, liq = calculate_risk_score(profile, m)
            db.add(RiskScore(protocol_id=protocol.id, risk_score=score, risk_level=level, volatility_score=vol_risk, liquidity_score=1 - liq, model_version="realistic_simulation_v1", timestamp=timestamp))
            risks_written += 1
            logger.info(f"{protocol.name:20s} | Risk: {score*100:5.1f}% ({level})")

        db.commit()
        logger.info("=" * 60)
        logger.info(f"✅ Wrote {metrics_written} metrics and {risks_written} risk scores (latest)")
        logger.info("✨ Refresh dashboard to see updated scores")


if __name__ == "__main__":
    main()



