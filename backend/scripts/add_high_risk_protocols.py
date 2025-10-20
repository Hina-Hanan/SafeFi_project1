"""
Add some protocols with high-risk characteristics for demonstration.
"""
import logging
import sys
import random
from datetime import datetime
from pathlib import Path
from decimal import Decimal

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolMetric, RiskScore
from sqlalchemy import select, func

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("scripts.add_high_risk")


def update_to_high_risk(protocol_name: str, risk_percentage: float):
    """Update a protocol to have high risk characteristics."""
    with managed_session() as db:
        protocol = db.execute(
            select(Protocol).where(Protocol.name == protocol_name)
        ).scalar_one_or_none()
        
        if not protocol:
            logger.warning(f"Protocol {protocol_name} not found")
            return False
        
        timestamp = datetime.utcnow()
        risk_score = risk_percentage / 100
        
        # Create high-risk metrics
        metrics = ProtocolMetric(
            protocol_id=protocol.id,
            tvl=Decimal(str(random.uniform(50_000_000, 500_000_000))),  # Lower TVL
            volume_24h=Decimal(str(random.uniform(10_000_000, 100_000_000))),  # Lower volume
            price=Decimal(str(random.uniform(0.5, 5))),
            market_cap=Decimal(str(random.uniform(30_000_000, 300_000_000))),
            price_change_24h=Decimal(str(random.uniform(-25, -15))),  # Large negative change
            timestamp=timestamp
        )
        db.add(metrics)
        
        # Create high risk score
        risk = RiskScore(
            protocol_id=protocol.id,
            risk_score=risk_score,
            risk_level="high",
            volatility_score=random.uniform(0.80, 0.95),  # High volatility
            liquidity_score=random.uniform(0.40, 0.60),   # Low liquidity
            model_version="realistic_simulation_v1",
            timestamp=timestamp
        )
        db.add(risk)
        
        db.commit()
        logger.info(f"🔴 {protocol_name:20s} | Updated to HIGH RISK: {risk_percentage}%")
        return True


def main():
    """Update some protocols to high risk."""
    logger.info("=" * 60)
    logger.info("🔴 Adding HIGH RISK protocols...")
    logger.info("=" * 60)
    
    # Make Uniswap high risk (due to high volatility)
    update_to_high_risk("Uniswap", random.uniform(72, 85))
    
    # Make SushiSwap high risk
    update_to_high_risk("SushiSwap", random.uniform(70, 78))
    
    # Make dYdX high risk
    update_to_high_risk("dYdX", random.uniform(73, 82))
    
    logger.info("=" * 60)
    logger.info("✅ High-risk protocols added!")
    logger.info("")
    logger.info("💡 Refresh your dashboard to see the updated data!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()


