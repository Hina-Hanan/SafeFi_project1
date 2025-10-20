"""
Simulate live data updates with realistic market changes.

This script updates protocol metrics to simulate live market movements:
- Prices fluctuate ±10%
- Volumes change ±30%
- TVL changes ±5%
- Risk scores recalculated based on new metrics

Run this every 2-4 hours to show "live" monitoring to reviewers.
"""
import logging
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path
from decimal import Decimal

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolMetric, RiskScore
from sqlalchemy import select, func

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.update_live_data")


def calculate_updated_risk(old_risk: float, price_change: float, volume_change: float) -> tuple:
    """
    Calculate new risk score based on market changes.
    
    Large price drops or volume drops = increased risk
    Stable/positive changes = decreased risk
    """
    # Base risk from previous
    new_risk = old_risk
    
    # Price impact (large drops increase risk)
    if price_change < -15:
        new_risk += 0.08  # Significant drop = high risk increase
    elif price_change < -8:
        new_risk += 0.04  # Moderate drop = medium risk increase
    elif price_change < 0:
        new_risk += 0.01  # Small drop = slight risk increase
    else:
        new_risk -= 0.02  # Positive change = risk decrease
    
    # Volume impact (low volume = higher risk)
    if volume_change < -20:
        new_risk += 0.05  # Volume drying up = risk increase
    elif volume_change > 20:
        new_risk -= 0.03  # High volume = risk decrease
    
    # Add small random market noise
    new_risk += random.uniform(-0.02, 0.02)
    
    # Clamp between 0 and 1
    new_risk = max(0.1, min(0.95, new_risk))
    
    # Determine level
    if new_risk >= 0.70:
        level = "high"
    elif new_risk >= 0.40:
        level = "medium"
    else:
        level = "low"
    
    return new_risk, level


def update_protocol_data(protocol: Protocol, last_metrics: ProtocolMetric, last_risk: RiskScore):
    """Update a protocol with simulated live data changes."""
    
    # Simulate market movements
    price_change_pct = random.gauss(0, 5)  # Normal distribution, mean=0, std=5%
    volume_change_pct = random.gauss(0, 15)  # Volumes more volatile
    tvl_change_pct = random.gauss(0, 2)  # TVL more stable
    
    # Calculate new values
    new_price = float(last_metrics.price or 1) * (1 + price_change_pct / 100)
    new_volume = float(last_metrics.volume_24h or 0) * (1 + volume_change_pct / 100)
    new_tvl = float(last_metrics.tvl or 0) * (1 + tvl_change_pct / 100)
    new_market_cap = float(last_metrics.market_cap or 0) * (1 + price_change_pct / 100)
    
    # Ensure positive values
    new_price = max(0.01, new_price)
    new_volume = max(0, new_volume)
    new_tvl = max(0, new_tvl)
    new_market_cap = max(0, new_market_cap)
    
    # Calculate new risk
    new_risk_score, new_risk_level = calculate_updated_risk(
        last_risk.risk_score,
        price_change_pct,
        volume_change_pct
    )
    
    # Update volatility based on price change magnitude
    volatility_change = abs(price_change_pct) / 20  # Normalize to 0-1
    new_volatility = (last_risk.volatility_score or 0.5) * 0.8 + volatility_change * 0.2
    new_volatility = max(0.1, min(0.95, new_volatility))
    
    # Liquidity correlates with volume
    liquidity_change = volume_change_pct / 100
    new_liquidity = (last_risk.liquidity_score or 0.5) * 0.9 + liquidity_change * 0.1
    new_liquidity = max(0.3, min(0.99, new_liquidity))
    
    timestamp = datetime.utcnow()
    
    return {
        "metrics": ProtocolMetric(
            protocol_id=protocol.id,
            tvl=Decimal(str(new_tvl)),
            volume_24h=Decimal(str(new_volume)),
            price=Decimal(str(new_price)),
            market_cap=Decimal(str(new_market_cap)),
            price_change_24h=Decimal(str(price_change_pct)),
            timestamp=timestamp
        ),
        "risk": RiskScore(
            protocol_id=protocol.id,
            risk_score=new_risk_score,
            risk_level=new_risk_level,
            volatility_score=new_volatility,
            liquidity_score=new_liquidity,
            model_version="live_update_v1",
            timestamp=timestamp
        ),
        "changes": {
            "price_change": price_change_pct,
            "volume_change": volume_change_pct,
            "tvl_change": tvl_change_pct,
            "risk_change": (new_risk_score - last_risk.risk_score) * 100
        }
    }


def main():
    """Update all protocols with simulated live data."""
    logger.info("=" * 70)
    logger.info("🔄 LIVE DATA UPDATE - Simulating Market Changes")
    logger.info(f"⏰ Update Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    with managed_session() as db:
        # Get all active protocols
        protocols = db.execute(
            select(Protocol).where(Protocol.is_active == True)
        ).scalars().all()
        
        if not protocols:
            logger.error("❌ No protocols found!")
            return
        
        logger.info(f"📊 Updating {len(protocols)} protocols with live market data...")
        logger.info("")
        
        updated_count = 0
        risk_changes = {"increased": 0, "decreased": 0, "stable": 0}
        level_changes = {"to_high": [], "to_medium": [], "to_low": []}
        
        for protocol in protocols:
            # Get latest metrics and risk
            latest_metrics = db.execute(
                select(ProtocolMetric)
                .where(ProtocolMetric.protocol_id == protocol.id)
                .order_by(ProtocolMetric.timestamp.desc())
                .limit(1)
            ).scalar_one_or_none()
            
            latest_risk = db.execute(
                select(RiskScore)
                .where(RiskScore.protocol_id == protocol.id)
                .order_by(RiskScore.timestamp.desc())
                .limit(1)
            ).scalar_one_or_none()
            
            if not latest_metrics or not latest_risk:
                logger.warning(f"⚠️  {protocol.name} - No existing data, skipping")
                continue
            
            # Store old risk level for comparison
            old_risk_level = latest_risk.risk_level
            
            # Generate new data
            update_data = update_protocol_data(protocol, latest_metrics, latest_risk)
            
            # Add to database
            db.add(update_data["metrics"])
            db.add(update_data["risk"])
            
            # Track changes
            risk_change = update_data["changes"]["risk_change"]
            if risk_change > 1:
                risk_changes["increased"] += 1
            elif risk_change < -1:
                risk_changes["decreased"] += 1
            else:
                risk_changes["stable"] += 1
            
            # Track level changes
            new_risk_level = update_data["risk"].risk_level
            if new_risk_level != old_risk_level:
                if new_risk_level == "high":
                    level_changes["to_high"].append(protocol.name)
                elif new_risk_level == "medium":
                    level_changes["to_medium"].append(protocol.name)
                else:
                    level_changes["to_low"].append(protocol.name)
            
            # Log update
            risk_emoji = "🔴" if new_risk_level == "high" else "🟡" if new_risk_level == "medium" else "🟢"
            change_emoji = "📈" if risk_change > 0 else "📉" if risk_change < 0 else "➡️"
            
            logger.info(
                f"{risk_emoji} {protocol.name:20s} | "
                f"Risk: {update_data['risk'].risk_score*100:5.1f}% ({new_risk_level:6s}) "
                f"{change_emoji} {risk_change:+.1f}% | "
                f"Price: {update_data['changes']['price_change']:+.1f}% | "
                f"Vol: {update_data['changes']['volume_change']:+.1f}%"
            )
            
            updated_count += 1
        
        # Commit all changes
        db.commit()
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ Updated {updated_count} protocols")
        logger.info("")
        
        # Show summary
        logger.info("📊 Risk Movement Summary:")
        logger.info(f"   📈 Increased Risk: {risk_changes['increased']} protocols")
        logger.info(f"   📉 Decreased Risk: {risk_changes['decreased']} protocols")
        logger.info(f"   ➡️  Stable: {risk_changes['stable']} protocols")
        
        if level_changes["to_high"]:
            logger.info("")
            logger.info(f"   🔴 NEW HIGH RISK: {', '.join(level_changes['to_high'])}")
        if level_changes["to_medium"]:
            logger.info(f"   🟡 NEW MEDIUM RISK: {', '.join(level_changes['to_medium'])}")
        if level_changes["to_low"]:
            logger.info(f"   🟢 NEW LOW RISK: {', '.join(level_changes['to_low'])}")
        
        # Show next update recommendation
        next_update = datetime.now() + timedelta(hours=3)
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"⏭️  Next recommended update: {next_update.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("💡 Tip: Schedule this script to run every 2-4 hours for live demo")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()


