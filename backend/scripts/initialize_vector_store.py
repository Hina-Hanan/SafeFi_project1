"""
Initialize Vector Store Script

This script initializes the vector store with database documents.
Run this script to manually initialize the RAG vector store for the LLM assistant.

Usage:
    python scripts/initialize_vector_store.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.services.rag.vector_store import initialize_vector_store, get_vector_store_manager
from app.database.models import Protocol, ProtocolMetric, RiskScore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Initialize vector store with database documents."""
    logger.info("=" * 50)
    logger.info("🚀 Vector Store Initialization Script")
    logger.info("=" * 50)
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Check database has data
        logger.info("📊 Checking database...")
        
        protocol_count = db.query(Protocol).count()
        metric_count = db.query(ProtocolMetric).count()
        risk_score_count = db.query(RiskScore).count()
        
        logger.info(f"  • Protocols: {protocol_count}")
        logger.info(f"  • Metrics: {metric_count}")
        logger.info(f"  • Risk Scores: {risk_score_count}")
        
        if protocol_count == 0:
            logger.warning("⚠️ No protocols found in database!")
            logger.info("💡 Run 'python scripts/seed_real_protocols.py' first to add protocol data")
            return
        
        # Initialize vector store
        logger.info("🔧 Initializing vector store...")
        
        manager = initialize_vector_store(db)
        
        if manager.vectorstore:
            logger.info("✅ Vector store initialized successfully!")
            
            # Get vector store manager
            vector_manager = get_vector_store_manager()
            
            # Show statistics
            logger.info("📊 Vector Store Statistics:")
            logger.info(f"  • Store Type: {'FAISS (in-memory)' if vector_manager.use_faiss else 'ChromaDB (persistent)'}")
            logger.info(f"  • Embedding Model: {vector_manager.embedding_model_name}")
            
            # Test query
            logger.info("🧪 Testing vector store with sample query...")
            test_results = vector_manager.similarity_search("high risk protocols", k=3)
            logger.info(f"  • Found {len(test_results)} relevant documents")
            
            if test_results:
                logger.info("  • Sample result:")
                logger.info(f"    {test_results[0].page_content[:200]}...")
            
            logger.info("")
            logger.info("=" * 50)
            logger.info("✅ Initialization Complete!")
            logger.info("=" * 50)
            logger.info("💡 The LLM assistant is now ready to use")
            logger.info("   Access it at: http://localhost:5173 (AI Assistant tab)")
            
        else:
            logger.error("❌ Failed to initialize vector store")
            logger.error("   Vector store is None after initialization")
            return
        
    except Exception as e:
        logger.error(f"❌ Error during initialization: {e}", exc_info=True)
        return
    finally:
        db.close()


if __name__ == "__main__":
    main()


