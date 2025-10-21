"""
Startup initialization script for the DeFi Risk Assessment backend.

This script runs on application startup to ensure all services are properly initialized,
including the vector store for RAG functionality.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.services.rag.vector_store import initialize_vector_store, get_vector_store_manager
from app.services.rag.llm_service import get_llm_service

logger = logging.getLogger(__name__)


def initialize_services() -> None:
    """
    Initialize all backend services on startup.
    
    This includes:
    - Vector store for RAG
    - LLM service
    - Database connections
    """
    logger.info("🚀 Initializing backend services...")
    
    # Initialize database session
    db: Session = SessionLocal()
    
    try:
        # Check if we have any protocols in the database
        from app.database.models import Protocol
        protocol_count = db.query(Protocol).count()
        
        logger.info(f"📊 Found {protocol_count} protocols in database")
        
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
        
        logger.info("✅ Backend services initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Error during service initialization: {e}")
    finally:
        db.close()


def cleanup_services() -> None:
    """
    Cleanup services on shutdown.
    """
    logger.info("🛑 Cleaning up backend services...")
    
    try:
        # Get vector store manager
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
    
    initialize_services()
    
    yield
    
    # Shutdown
    logger.info("=" * 50)
    logger.info("🛑 DeFi Risk Assessment Backend Shutting Down")
    logger.info("=" * 50)
    
    cleanup_services()


