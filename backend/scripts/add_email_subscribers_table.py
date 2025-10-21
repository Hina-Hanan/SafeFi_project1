"""
Database migration script to add EmailSubscriber table.

Run this script to add the email_subscribers table to the database.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from sqlalchemy import text

from app.database.connection import SessionLocal
from app.database.models import Base, EmailSubscriber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Add EmailSubscriber table to database."""
    logger.info("=" * 50)
    logger.info("🔧 Database Migration: Add EmailSubscriber Table")
    logger.info("=" * 50)
    
    db = SessionLocal()
    
    try:
        # Check if table exists
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='email_subscribers')"
        ))
        table_exists = result.scalar()
        
        if table_exists:
            logger.info("✅ Table 'email_subscribers' already exists")
            return
        
        # Create table
        logger.info("📊 Creating 'email_subscribers' table...")
        
        # Import engine from connection
        from app.database.connection import ENGINE as engine
        
        # Create only the EmailSubscriber table
        EmailSubscriber.__table__.create(engine, checkfirst=True)
        
        logger.info("✅ Table 'email_subscribers' created successfully")
        
        # Verify table was created
        result = db.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='email_subscribers')"
        ))
        table_exists = result.scalar()
        
        if table_exists:
            logger.info("✅ Verification: Table exists in database")
            
            # Show table structure
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'email_subscribers'
                ORDER BY ordinal_position
            """))
            
            logger.info("\n📋 Table Structure:")
            for row in result:
                logger.info(f"  • {row[0]}: {row[1]} (nullable: {row[2]})")
        else:
            logger.error("❌ Table creation verification failed")
            return
        
        logger.info("")
        logger.info("=" * 50)
        logger.info("✅ Migration Completed Successfully!")
        logger.info("=" * 50)
        logger.info("💡 Users can now subscribe to email alerts via the frontend")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        return
    finally:
        db.close()


if __name__ == "__main__":
    main()


