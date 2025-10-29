"""
Complete Database Setup Script
Executes all necessary steps to initialize the database with tables, protocols, metrics, and risk scores.
"""
import sys
import logging
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database.connection import ENGINE
from app.database.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("complete_db_setup")


def main():
    """Run complete database setup."""
    logger.info("=" * 80)
    logger.info("🚀 COMPLETE DATABASE SETUP - START")
    logger.info("=" * 80)
    
    # Step 1: Create all tables
    logger.info("\n📋 Step 1: Creating database tables from models.py...")
    try:
        Base.metadata.create_all(bind=ENGINE, checkfirst=True)
        logger.info("✅ All tables created successfully")
        
        # List tables
        from sqlalchemy import inspect
        inspector = inspect(ENGINE)
        tables = inspector.get_table_names()
        logger.info(f"   Tables: {', '.join(tables)}")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return 1
    
    # Step 2: Seed protocols (already done, but verify)
    logger.info("\n📊 Step 2: Verifying protocols...")
    from app.database.connection import managed_session
    from app.database.models import Protocol
    try:
        with managed_session() as db:
            count = db.query(Protocol).count()
            logger.info(f"✅ Found {count} protocols in database")
            if count == 0:
                logger.warning("⚠️  No protocols found. Run: python scripts/seed_real_protocols.py")
    except Exception as e:
        logger.error(f"❌ Error checking protocols: {e}")
    
    # Step 3: Generate metrics data
    logger.info("\n📈 Step 3: Generating protocol metrics...")
    try:
        import scripts.real_data as real_data_module
        real_data_module.main()
        logger.info("✅ Protocol metrics generated")
    except Exception as e:
        logger.error(f"❌ Failed to generate metrics: {e}")
        logger.info("   You can run manually: python scripts/real_data.py")
    
    # Step 4: Calculate risk scores
    logger.info("\n🎯 Step 4: Calculating risk scores...")
    try:
        import scripts.auto_update_risks as risk_module
        risk_module.main()
        logger.info("✅ Risk scores calculated")
    except Exception as e:
        logger.error(f"❌ Failed to calculate risks: {e}")
        logger.info("   You can run manually: python scripts/auto_update_risks.py")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ COMPLETE DATABASE SETUP - FINISHED")
    logger.info("=" * 80)
    logger.info("\n📊 Database Status:")
    try:
        with managed_session() as db:
            from app.database.models import Protocol, ProtocolMetric, RiskScore
            protocol_count = db.query(Protocol).count()
            metric_count = db.query(ProtocolMetric).count()
            risk_count = db.query(RiskScore).count()
            logger.info(f"   • Protocols: {protocol_count}")
            logger.info(f"   • Metrics: {metric_count}")
            logger.info(f"   • Risk Scores: {risk_count}")
    except Exception as e:
        logger.warning(f"   Could not fetch counts: {e}")
    
    logger.info("\n🎉 Backend is ready for use!")
    logger.info("   • API: http://localhost:8000")
    logger.info("   • Health: http://localhost:8000/health")
    logger.info("   • Docs: http://localhost:8000/docs")
    logger.info("   • Scheduler: Running automatically every 15-30 minutes")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


