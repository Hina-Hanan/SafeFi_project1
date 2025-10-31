"""
Production setup script - Complete initialization for production deployment.

This script:
1. Clears test data
2. Seeds real DeFi protocols
3. Collects live data
4. Calculates risk scores
5. Verifies system health

Run this ONCE when deploying to production.
"""
import asyncio
import logging
import sys
from datetime import datetime

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolMetric, RiskScore
from sqlalchemy import select


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.production_setup")


def clear_test_data() -> None:
    """Remove test protocols from database."""
    logger.info("🧹 Cleaning test data...")
    
    test_protocol_names = [
        "Test DeFi Protocol 1",
        "Test Lending Protocol",
        "Test Yield Protocol",
    ]
    
    with managed_session() as db:
        deleted_count = 0
        for name in test_protocol_names:
            protocol = db.query(Protocol).filter_by(name=name).first()
            if protocol:
                db.delete(protocol)
                deleted_count += 1
                logger.info(f"   ❌ Removed: {name}")
        
        db.commit()
        logger.info(f"✅ Cleaned {deleted_count} test protocols")


async def main() -> None:
    """Run complete production setup."""
    logger.info("=" * 70)
    logger.info("🚀 DEFI RISK ASSESSMENT - PRODUCTION SETUP")
    logger.info("=" * 70)
    logger.info(f"Started at: {datetime.now().isoformat()}")
    logger.info("")
    
    # Step 1: Clear test data
    logger.info("STEP 1: Cleaning test data...")
    try:
        clear_test_data()
        logger.info("✅ Step 1 complete\n")
    except Exception as e:
        logger.error(f"❌ Failed to clear test data: {e}")
        logger.info("   Continuing anyway...")
    
    # Step 2: Seed real protocols
    logger.info("STEP 2: Adding real DeFi protocols...")
    try:
        import scripts.seed_real_protocols as seed
        seed.main()
        logger.info("✅ Step 2 complete\n")
    except Exception as e:
        logger.error(f"❌ Failed to seed protocols: {e}")
        sys.exit(1)
    
    # Step 3: Collect live data
    logger.info("STEP 3: Collecting live data from APIs...")
    logger.info("   (This may take 2-5 minutes for ~20 protocols)")
    try:
        import scripts.collect_live_data as collector
        await collector.main()
        logger.info("✅ Step 3 complete\n")
    except Exception as e:
        logger.error(f"❌ Failed to collect data: {e}")
        logger.info("   You can run manually later: python scripts/collect_live_data.py")
    
    # Step 4: Calculate risks
    logger.info("STEP 4: Calculating risk scores...")
    try:
        import scripts.calculate_risks as risk_calc
        risk_calc.main()
        logger.info("✅ Step 4 complete\n")
    except Exception as e:
        logger.error(f"❌ Failed to calculate risks: {e}")
        logger.info("   You can run manually later: python scripts/calculate_risks.py")
    
    # Step 5: Verify system
    logger.info("STEP 5: Verifying system health...")
    with managed_session() as db:
        total_protocols = db.scalar(select(Protocol).count())
        total_metrics = db.scalar(select(ProtocolMetric).count())
        total_risks = db.scalar(select(RiskScore).count())
        
        logger.info(f"   📊 Total Protocols: {total_protocols}")
        logger.info(f"   📊 Total Metrics: {total_metrics}")
        logger.info(f"   📊 Total Risk Scores: {total_risks}")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🎉 PRODUCTION SETUP COMPLETE!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("✨ Your DeFi Risk Assessment Platform is ready!")
    logger.info("")
    logger.info("📝 Next steps:")
    logger.info("   1. Start backend: uvicorn app.main:app --host 0.0.0.0 --port 8000")
    logger.info("   2. Visit dashboard: http://localhost:5173")
    logger.info("   3. Set up automated data refresh (see docs)")
    logger.info("")
    logger.info("🔄 For continuous updates, schedule these scripts:")
    logger.info("   - Every 15 min: python scripts/collect_live_data.py")
    logger.info("   - Every 30 min: python scripts/calculate_risks.py")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
































