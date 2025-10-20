"""
Collect live data from CoinGecko and DeFiLlama for all active protocols.

This script should be run periodically (every 15-30 minutes) to keep
data fresh and up-to-date for real-time risk assessment.
"""
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import managed_session
from app.services.data_collector import DataCollectorService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.collect_live_data")


async def main() -> None:
    """Collect live data from external APIs."""
    logger.info("=" * 60)
    logger.info("🔄 Starting live data collection...")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    with managed_session() as db:
        service = DataCollectorService(db=db)
        
        # Collect from CoinGecko (price, market cap, price changes)
        logger.info("📊 Collecting from CoinGecko...")
        try:
            cg_count = await service.collect(source="coingecko", protocol_ids=None)
            logger.info(f"✅ CoinGecko: Successfully processed {cg_count} protocols")
        except Exception as e:
            logger.error(f"❌ CoinGecko collection failed: {e}")
            cg_count = 0
        
        # Collect from DeFiLlama (TVL data)
        logger.info("📊 Collecting from DeFiLlama...")
        try:
            ll_count = await service.collect(source="defillama", protocol_ids=None)
            logger.info(f"✅ DeFiLlama: Successfully processed {ll_count} protocols")
        except Exception as e:
            logger.error(f"❌ DeFiLlama collection failed: {e}")
            ll_count = 0
        
        db.commit()
    
    logger.info("=" * 60)
    logger.info(f"📈 Total protocols updated: {max(cg_count, ll_count)}")
    logger.info("🎉 Live data collection completed!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next: Run risk calculation: python scripts/calculate_risks.py")


if __name__ == "__main__":
    asyncio.run(main())




