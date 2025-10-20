"""
Generate 7-day historical risk data for all protocols.

Creates realistic historical data points (4 per day = 28 total points) 
to show meaningful trends in the 7-Day Analysis chart.
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
from sqlalchemy import select

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.generate_7day_history")


def generate_historical_trend(base_risk: float, days: int = 7, points_per_day: int = 4):
    """
    Generate realistic risk score trend over time.
    
    Simulates:
    - Gradual trends (increasing or decreasing risk)
    - Random market noise
    - Some protocols stable, some volatile
    """
    total_points = days * points_per_day
    timestamps = []
    risk_scores = []
    
    # Decide trend direction
    trend_type = random.choice(['increasing', 'decreasing', 'stable', 'volatile'])
    
    for i in range(total_points):
        # Calculate time (going backwards from now)
        hours_ago = (total_points - i) * (24 / points_per_day)
        timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
        timestamps.append(timestamp)
        
        # Calculate risk score based on trend type
        progress = i / total_points  # 0 to 1
        
        if trend_type == 'increasing':
            # Risk gradually increases
            risk_change = progress * random.uniform(0.15, 0.25)  # +15-25% over period
            risk_score = base_risk + risk_change
            
        elif trend_type == 'decreasing':
            # Risk gradually decreases
            risk_change = progress * random.uniform(0.15, 0.25)
            risk_score = base_risk - risk_change
            
        elif trend_type == 'stable':
            # Risk stays mostly stable with small noise
            risk_score = base_risk + random.uniform(-0.03, 0.03)
            
        else:  # volatile
            # Risk fluctuates significantly
            risk_score = base_risk + random.gauss(0, 0.08)
        
        # Add daily noise
        risk_score += random.gauss(0, 0.02)
        
        # Clamp to valid range
        risk_score = max(0.10, min(0.95, risk_score))
        risk_scores.append(risk_score)
    
    return timestamps, risk_scores, trend_type


def generate_metrics_for_risk(base_tvl: float, risk_score: float):
    """Generate protocol metrics that correlate with risk score."""
    # Higher risk = more volatile prices, lower volumes
    volatility = risk_score * random.uniform(0.8, 1.2)
    
    # Simulate price change based on risk
    if risk_score > 0.7:  # High risk
        price_change = random.gauss(-8, 10)
    elif risk_score > 0.4:  # Medium risk
        price_change = random.gauss(0, 5)
    else:  # Low risk
        price_change = random.gauss(2, 3)
    
    tvl_change = random.gauss(0, 2)
    volume_change = random.gauss(0, 10)
    
    return {
        'tvl': base_tvl * (1 + tvl_change / 100),
        'volume': base_tvl * (0.3 + (1 - risk_score) * 0.4) * (1 + volume_change / 100),
        'price': 1.0 * (1 + price_change / 100),
        'price_change': price_change,
        'volatility': volatility,
        'liquidity': 1 - risk_score * random.uniform(0.8, 1.2)
    }


def main():
    """Generate 7-day history for all protocols."""
    logger.info("=" * 70)
    logger.info("📅 Generating 7-Day Historical Data for All Protocols")
    logger.info(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    with managed_session() as db:
        # Get all active protocols
        protocols = db.execute(
            select(Protocol).where(Protocol.is_active == True)
        ).scalars().all()
        
        if not protocols:
            logger.error("❌ No protocols found!")
            return
        
        logger.info(f"📊 Found {len(protocols)} protocols")
        logger.info(f"🔧 Generating 7 days × 4 points/day = 28 data points per protocol")
        logger.info("")
        
        total_metrics = 0
        total_risks = 0
        
        for protocol in protocols:
            # Get current risk score as base
            latest_risk = db.execute(
                select(RiskScore)
                .where(RiskScore.protocol_id == protocol.id)
                .order_by(RiskScore.timestamp.desc())
                .limit(1)
            ).scalar_one_or_none()
            
            if not latest_risk:
                logger.warning(f"⚠️  {protocol.name} - No risk score, skipping")
                continue
            
            base_risk = latest_risk.risk_score
            
            # Get base TVL for metrics
            latest_metrics = db.execute(
                select(ProtocolMetric)
                .where(ProtocolMetric.protocol_id == protocol.id)
                .order_by(ProtocolMetric.timestamp.desc())
                .limit(1)
            ).scalar_one_or_none()
            
            base_tvl = float(latest_metrics.tvl) if latest_metrics and latest_metrics.tvl else 100_000_000
            
            # Generate historical trend
            timestamps, risk_scores, trend_type = generate_historical_trend(base_risk)
            
            # Create database entries for each point
            for timestamp, risk_score in zip(timestamps, risk_scores):
                # Generate correlated metrics
                metrics_data = generate_metrics_for_risk(base_tvl, risk_score)
                
                # Create metric record
                metric = ProtocolMetric(
                    protocol_id=protocol.id,
                    tvl=Decimal(str(metrics_data['tvl'])),
                    volume_24h=Decimal(str(metrics_data['volume'])),
                    price=Decimal(str(metrics_data['price'])),
                    market_cap=Decimal(str(base_tvl * 1.2)),
                    price_change_24h=Decimal(str(metrics_data['price_change'])),
                    timestamp=timestamp
                )
                db.add(metric)
                total_metrics += 1
                
                # Determine risk level
                if risk_score >= 0.70:
                    risk_level = "high"
                elif risk_score >= 0.40:
                    risk_level = "medium"
                else:
                    risk_level = "low"
                
                # Create risk score record
                risk = RiskScore(
                    protocol_id=protocol.id,
                    risk_score=risk_score,
                    risk_level=risk_level,
                    volatility_score=max(0.1, min(0.95, metrics_data['volatility'])),
                    liquidity_score=max(0.3, min(0.99, metrics_data['liquidity'])),
                    model_version="historical_7day_v1",
                    timestamp=timestamp
                )
                db.add(risk)
                total_risks += 1
            
            # Calculate trend info
            start_risk = risk_scores[0] * 100
            end_risk = risk_scores[-1] * 100
            change = end_risk - start_risk
            
            trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            risk_emoji = "🔴" if end_risk >= 70 else "🟡" if end_risk >= 40 else "🟢"
            
            logger.info(
                f"{risk_emoji} {protocol.name:20s} | "
                f"Trend: {trend_type:12s} {trend_emoji} | "
                f"7d: {start_risk:5.1f}% → {end_risk:5.1f}% ({change:+.1f}%) | "
                f"Points: 28"
            )
        
        # Commit all data
        db.commit()
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✅ Created {total_metrics} metrics and {total_risks} risk scores")
        logger.info(f"📊 Total data points: {total_risks // len(protocols)} per protocol")
        logger.info("")
        logger.info("💡 Refresh your 7-Day Analysis tab to see the trends!")
        logger.info("=" * 70)


if __name__ == "__main__":
    main()


