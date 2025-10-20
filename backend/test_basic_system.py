#!/usr/bin/env python3
"""
Basic test script for the ML Risk Scoring System.

This simplified version tests core functionality without requiring all ML dependencies.
"""

import logging
import os
import sys
from datetime import datetime, timedelta

# Set up environment variables if not already set
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment'

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_imports():
    """Test if basic imports work."""
    logger.info("Testing basic imports...")
    
    try:
        from app.database.connection import SessionLocal, ENGINE
        logger.info("✅ Database connection import successful")
        
        from app.database.models import Protocol, ProtocolMetric, RiskScore
        logger.info("✅ Database models import successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic imports failed: {e}")
        return False


def test_database_connection():
    """Test database connectivity."""
    logger.info("Testing database connection...")
    
    try:
        from app.database.connection import SessionLocal
        
        db = SessionLocal()
        try:
            # Test basic query
            from sqlalchemy import text
            result = db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("✅ Database connection test successful")
                return True
            else:
                logger.error("❌ Database query returned unexpected result")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        logger.info("Make sure PostgreSQL is running and accessible")
        return False


def test_protocol_data():
    """Test if protocol data exists in database."""
    logger.info("Testing protocol data...")
    
    try:
        from app.database.connection import SessionLocal
        from app.database.models import Protocol, ProtocolMetric
        
        db = SessionLocal()
        try:
            # Check for protocols
            protocol_count = db.query(Protocol).count()
            logger.info(f"Found {protocol_count} protocols in database")
            
            # Check for metrics
            metric_count = db.query(ProtocolMetric).count()
            logger.info(f"Found {metric_count} protocol metrics in database")
            
            if protocol_count > 0 and metric_count > 0:
                logger.info("✅ Protocol data test successful")
                return True
            else:
                logger.warning("⚠️ No protocol data found - run data collection first")
                return False
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Protocol data test failed: {e}")
        return False


def test_api_structure():
    """Test if API structure is correct."""
    logger.info("Testing API structure...")
    
    try:
        from app.api.v1 import ml
        logger.info("✅ ML API module import successful")
        
        # Check if key endpoints exist
        if hasattr(ml, 'router') and hasattr(ml, 'risk_router'):
            logger.info("✅ API routers found")
            return True
        else:
            logger.error("❌ API routers not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ API structure test failed: {e}")
        return False


def test_ml_system_structure():
    """Test if ML system structure is in place (without actually running ML code)."""
    logger.info("Testing ML system structure...")
    
    try:
        # Test if risk calculator module exists
        import importlib.util
        
        risk_calc_path = os.path.join(os.path.dirname(__file__), 'app', 'services', 'risk_calculator.py')
        if os.path.exists(risk_calc_path):
            logger.info("✅ Risk calculator module exists")
            
            # Check if the file contains key classes/functions
            with open(risk_calc_path, 'r') as f:
                content = f.read()
                
            required_items = [
                'class RiskCalculatorService',
                'def train_models',
                'def predict_protocol',
                'def predict_batch',
                'FEATURE_COLUMNS'
            ]
            
            missing_items = []
            for item in required_items:
                if item not in content:
                    missing_items.append(item)
            
            if not missing_items:
                logger.info("✅ All required ML components found in risk calculator")
                return True
            else:
                logger.error(f"❌ Missing ML components: {missing_items}")
                return False
        else:
            logger.error("❌ Risk calculator module not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ ML system structure test failed: {e}")
        return False


def main():
    """Run basic system tests."""
    logger.info("🚀 Starting Basic ML Risk Scoring System Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Database Connection", test_database_connection),
        ("Protocol Data", test_protocol_data),
        ("API Structure", test_api_structure),
        ("ML System Structure", test_ml_system_structure),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"{test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 BASIC TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        logger.info(f"{test_name:<20} {status}")
        if passed_test:
            passed += 1
    
    logger.info("-" * 60)
    logger.info(f"TOTAL: {passed}/{total} basic tests passed")
    
    if passed == total:
        logger.info("🎉 All basic tests passed! System structure is correct.")
        logger.info("\nNext steps:")
        logger.info("1. Install ML dependencies: pip install mlflow scikit-learn xgboost")
        logger.info("2. Start docker services: docker-compose up -d")
        logger.info("3. Run full ML tests: python test_ml_system.py")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} basic tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
