"""
Startup initialization script for the DeFi Risk Assessment backend.

This script runs on application startup to ensure all services are properly initialized,
including the vector store for RAG functionality.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session
import os

from app.database.connection import SessionLocal
from app.services.automated_scheduler import get_scheduler

# Optional RAG imports (not available in slim API build)
try:
    from app.services.rag.vector_store import initialize_vector_store, get_vector_store_manager
    from app.services.rag.llm_service import get_llm_service
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("RAG/LLM dependencies not installed - running in API-only mode")

logger = logging.getLogger(__name__)


async def initialize_services() -> None:
    """
    Initialize all backend services on startup.
    
    This includes:
    - Vector store for RAG
    - LLM service
    - Database connections
    - Automated scheduler for data updates and alerts
    """
    logger.info("🚀 Initializing backend services...")
    
    # Initialize database session
    db: Session = SessionLocal()
    
    try:
        # Ensure database schema exists (create tables on first run)
        from app.database.models import Base, Protocol
        from app.database.connection import ENGINE

        try:
            Base.metadata.create_all(bind=ENGINE)
            logger.info("✅ Database tables ensured (created if missing)")
        except Exception as e:
            logger.error(f"❌ Failed to ensure database tables: {e}")

        # Optional seeding of initial protocols for first run
        try:
            should_seed = os.getenv("SEED_PROTOCOLS", "false").lower() in ("1", "true", "yes")
            protocol_count_existing = db.query(Protocol).count()
            if should_seed and protocol_count_existing == 0:
                seed_items = [
                    Protocol(name="Uniswap", symbol="UNI", category="dex", chain="ethereum", is_active=True),
                    Protocol(name="Aave", symbol="AAVE", category="lending", chain="ethereum", is_active=True),
                    Protocol(name="Curve", symbol="CRV", category="dex", chain="ethereum", is_active=True),
                ]
                db.add_all(seed_items)
                db.commit()
                logger.info(f"🌱 Seeded {len(seed_items)} initial protocols")
        except Exception as e:
            logger.error(f"❌ Failed to seed initial protocols: {e}")

        # Check if we have any protocols in the database
        from app.database.models import Protocol
        protocol_count = db.query(Protocol).count()
        
        logger.info(f"📊 Found {protocol_count} protocols in database")
        
        if RAG_AVAILABLE:
            if protocol_count > 0:
                # Initialize vector store automatically
                logger.info("🔧 Initializing vector store...")
                try:
                    manager = initialize_vector_store(db)
                    if manager.vectorstore:
                        logger.info("✅ Vector store initialized successfully")
                    else:
                        logger.warning("⚠️ Vector store initialization completed but vectorstore is None")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize vector store: {e}")
                    logger.warning("⚠️ LLM assistant will not be available until vector store is initialized")
            else:
                logger.warning("⚠️ No protocols found in database. Vector store will be initialized after data is added.")
                logger.info("💡 Run 'python scripts/seed_real_protocols.py' to add protocol data")
            
            # Initialize LLM service
            try:
                llm_service = get_llm_service()
                logger.info(f"✅ LLM service initialized with model: {llm_service.model}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LLM service: {e}")
        else:
            logger.info("ℹ️ RAG/LLM features disabled (slim API build)")
        
        # Initialize automated scheduler
        try:
            scheduler = get_scheduler()
            await scheduler.start()
            logger.info("✅ Automated scheduler started (15-30 minute intervals)")
        except Exception as e:
            logger.error(f"❌ Failed to start automated scheduler: {e}")
            logger.warning("⚠️ Automatic updates and alerts will not run")
        
        logger.info("✅ Backend services initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Error during service initialization: {e}")
    finally:
        db.close()


async def cleanup_services() -> None:
    """
    Cleanup services on shutdown.
    """
    logger.info("🛑 Cleaning up backend services...")
    
    try:
        # Stop automated scheduler
        try:
            scheduler = get_scheduler()
            await scheduler.stop()
            logger.info("✅ Automated scheduler stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping scheduler: {e}")
        
        # Get vector store manager (only if RAG is available)
        if RAG_AVAILABLE:
            manager = get_vector_store_manager()
            
            # If using FAISS (in-memory), we can clear it
            if manager.use_faiss and manager.vectorstore:
                logger.info("Clearing in-memory vector store")
                manager.vectorstore = None
        
        logger.info("✅ Service cleanup completed")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("=" * 50)
    logger.info("🚀 DeFi Risk Assessment Backend Starting Up")
    logger.info("=" * 50)
    
    await initialize_services()
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info("🛑 DeFi Risk Assessment Backend Shutting Down")
    logger.info("=" * 50)
    
    await cleanup_services()


