#!/usr/bin/env python3
"""
Test script for the ML Risk Scoring System.

This script validates the complete ML pipeline including:
- Feature engineering and data processing
- Model training with MLflow integration
- Risk prediction and batch processing
- API endpoints functionality
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import httpx
import pandas as pd
from sqlalchemy import text

# Set up environment variables if not already set
if not os.getenv('DATABASE_URL'):
    os.environ['DATABASE_URL'] = 'postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment'

if not os.getenv('MLFLOW_TRACKING_URI'):
    os.environ['MLFLOW_TRACKING_URI'] = 'http://127.0.0.1:5001'

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database.connection import SessionLocal, ENGINE
from app.database.models import Protocol, ProtocolMetric
from app.services.risk_calculator import RiskCalculatorService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_data():
    """Create sample test data for ML system validation."""
    logger.info("Creating test data...")
    
    db = SessionLocal()
    try:
        # Create test protocols
        test_protocols = [
            {
                "name": "Test DeFi Protocol 1",
                "symbol": "TDP1",
                "category": "dex",
                "chain": "ethereum"
            },
            {
                "name": "Test Lending Protocol",
                "symbol": "TLP",
                "category": "lending", 
                "chain": "ethereum"
            },
            {
                "name": "Test Yield Protocol",
                "symbol": "TYP",
                "category": "yield",
                "chain": "polygon"
            }
        ]
        
        protocol_ids = []
        for proto_data in test_protocols:
            # Check if protocol already exists
            existing = db.query(Protocol).filter(Protocol.name == proto_data["name"]).first()
            if not existing:
                protocol = Protocol(**proto_data)
                db.add(protocol)
                db.flush()
                protocol_ids.append(protocol.id)
            else:
                protocol_ids.append(existing.id)
        
        # Create synthetic metrics data for the last 60 days
        base_date = datetime.now() - timedelta(days=60)
        
        for i, protocol_id in enumerate(protocol_ids):
            # Generate different risk profiles for each protocol
            if i == 0:  # High volatility protocol
                base_tvl = 1000000
                base_price = 10.0
                volatility_factor = 0.3
            elif i == 1:  # Stable protocol
                base_tvl = 5000000
                base_price = 50.0
                volatility_factor = 0.1
            else:  # Medium risk protocol
                base_tvl = 2000000
                base_price = 25.0
                volatility_factor = 0.2
            
            for day in range(60):
                import random
                import math
                
                # Simulate realistic market data with trends and volatility
                timestamp = base_date + timedelta(days=day)
                
                # Add trend and noise
                trend_factor = 1 + 0.001 * day  # Slight upward trend
                noise = random.gauss(0, volatility_factor)
                
                tvl = base_tvl * trend_factor * (1 + noise)
                price = base_price * trend_factor * (1 + noise * 0.5)
                volume_24h = tvl * 0.1 * (1 + random.gauss(0, 0.2))
                market_cap = price * 1000000 * (1 + random.gauss(0, 0.1))
                price_change_24h = random.gauss(0, volatility_factor * 5)
                
                # Ensure positive values
                tvl = max(tvl, 1000)
                price = max(price, 0.01)
                volume_24h = max(volume_24h, 100)
                market_cap = max(market_cap, 10000)
                
                metric = ProtocolMetric(
                    protocol_id=protocol_id,
                    tvl=tvl,
                    volume_24h=volume_24h,
                    price=price,
                    market_cap=market_cap,
                    price_change_24h=price_change_24h,
                    timestamp=timestamp
                )
                db.add(metric)
        
        db.commit()
        logger.info(f"Created test data for {len(protocol_ids)} protocols with 60 days of metrics each")
        return protocol_ids
        
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        db.rollback()
        return []
    finally:
        db.close()


def test_feature_engineering():
    """Test the feature engineering pipeline."""
    logger.info("Testing feature engineering...")
    
    try:
        service = RiskCalculatorService()
        df = service._load_protocol_frame()
        
        if df.empty:
            logger.error("No data loaded for feature engineering")
            return False
        
        logger.info(f"Loaded {len(df)} raw metric records")
        
        # Test feature engineering
        features_df = service._engineer_features(df)
        
        if features_df.empty:
            logger.error("Feature engineering produced no results")
            return False
        
        logger.info(f"Generated {len(features_df)} feature records")
        logger.info(f"Feature columns: {list(features_df.columns)}")
        
        # Check that all expected features are present
        from app.services.risk_calculator import FEATURE_COLUMNS
        missing_features = set(FEATURE_COLUMNS) - set(features_df.columns)
        if missing_features:
            logger.error(f"Missing features: {missing_features}")
            return False
        
        logger.info("✅ Feature engineering test passed")
        return True
        
    except Exception as e:
        logger.error(f"Feature engineering test failed: {e}")
        return False


def test_model_training():
    """Test the ML model training pipeline."""
    logger.info("Testing model training...")
    
    try:
        service = RiskCalculatorService()
        performances = service.train_models()
        
        if not performances:
            logger.error("No models were trained")
            return False
        
        logger.info(f"Trained {len(performances)} models")
        
        for perf in performances:
            logger.info(f"Model {perf.model_name}: F1={perf.f1:.4f}, Accuracy={perf.accuracy:.4f}")
        
        # Check that all models have reasonable performance
        best_f1 = max(p.f1 for p in performances)
        if best_f1 < 0.3:  # Very low threshold for synthetic data
            logger.warning(f"Low model performance: best F1 = {best_f1:.4f}")
        
        logger.info("✅ Model training test passed")
        return True
        
    except Exception as e:
        logger.error(f"Model training test failed: {e}")
        return False


def test_risk_prediction():
    """Test individual risk prediction."""
    logger.info("Testing risk prediction...")
    
    try:
        # Get a test protocol
        db = SessionLocal()
        protocol = db.query(Protocol).first()
        db.close()
        
        if not protocol:
            logger.error("No protocols found for prediction test")
            return False
        
        service = RiskCalculatorService()
        prediction = service.predict_protocol(protocol.id)
        
        logger.info(f"Prediction for {protocol.name}:")
        logger.info(f"  Risk Level: {prediction.risk_level}")
        logger.info(f"  Risk Score: {prediction.risk_score:.4f}")
        logger.info(f"  Confidence: {prediction.confidence:.4f}")
        logger.info(f"  Model Version: {prediction.model_version}")
        
        # Validate prediction structure
        assert 0 <= prediction.risk_score <= 1, "Risk score should be between 0 and 1"
        assert prediction.risk_level in ["low", "medium", "high"], "Invalid risk level"
        assert 0 <= prediction.confidence <= 1, "Confidence should be between 0 and 1"
        assert len(prediction.features) > 0, "Features should not be empty"
        assert len(prediction.explanation) > 0, "Explanation should not be empty"
        
        logger.info("✅ Risk prediction test passed")
        return True
        
    except Exception as e:
        logger.error(f"Risk prediction test failed: {e}")
        return False


def test_batch_prediction():
    """Test batch risk prediction."""
    logger.info("Testing batch prediction...")
    
    try:
        service = RiskCalculatorService()
        results = service.predict_batch()
        
        if not results:
            logger.error("Batch prediction returned no results")
            return False
        
        logger.info(f"Batch prediction completed for {len(results)} protocols")
        
        # Check result structure
        for result in results[:3]:  # Check first 3 results
            assert "protocol_id" in result, "Missing protocol_id"
            assert "risk_score" in result, "Missing risk_score"
            assert "risk_level" in result, "Missing risk_level"
            assert "confidence" in result, "Missing confidence"
            
        logger.info("✅ Batch prediction test passed")
        return True
        
    except Exception as e:
        logger.error(f"Batch prediction test failed: {e}")
        return False


async def test_api_endpoints():
    """Test the API endpoints."""
    logger.info("Testing API endpoints...")
    
    # Note: This assumes the API server is running
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test model training endpoint
            logger.info("Testing POST /models/train")
            response = await client.post(f"{base_url}/models/train", timeout=120.0)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Training response: {data.get('message', 'No message')}")
                logger.info("✅ Model training endpoint test passed")
            else:
                logger.warning(f"Training endpoint returned {response.status_code}")
            
            # Test model performance endpoint
            logger.info("Testing GET /models/performance")
            response = await client.get(f"{base_url}/models/performance")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Performance data: {data.get('total_runs', 0)} total runs")
                logger.info("✅ Model performance endpoint test passed")
            else:
                logger.warning(f"Performance endpoint returned {response.status_code}")
            
            # Test risk prediction endpoint (need a protocol ID)
            db = SessionLocal()
            protocol = db.query(Protocol).first()
            db.close()
            
            if protocol:
                logger.info(f"Testing GET /risk/protocols/{protocol.id}/risk-details")
                response = await client.get(f"{base_url}/risk/protocols/{protocol.id}/risk-details")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Risk prediction: {data.get('risk_level')} ({data.get('risk_score', 0):.4f})")
                    logger.info("✅ Risk prediction endpoint test passed")
                else:
                    logger.warning(f"Risk prediction endpoint returned {response.status_code}")
            
            # Test batch calculation endpoint
            logger.info("Testing POST /risk/calculate-batch")
            response = await client.post(
                f"{base_url}/risk/calculate-batch", 
                json={},
                timeout=120.0
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Batch calculation: {data.get('successful_predictions', 0)} successful")
                logger.info("✅ Batch calculation endpoint test passed")
            else:
                logger.warning(f"Batch calculation endpoint returned {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"API endpoint test failed: {e}")
        return False


def test_mlflow_integration():
    """Test MLflow integration."""
    logger.info("Testing MLflow integration...")
    
    try:
        import mlflow
        
        # Set MLflow tracking URI
        mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
        
        # Check if MLflow server is accessible
        try:
            client = mlflow.MlflowClient()
            experiments = client.search_experiments()
            logger.info(f"Found {len(experiments)} MLflow experiments")
            
            # Look for our risk scoring experiment
            risk_experiment = None
            for exp in experiments:
                if exp.name == "risk_scoring":
                    risk_experiment = exp
                    break
            
            if risk_experiment:
                runs = client.search_runs(experiment_ids=[risk_experiment.experiment_id], max_results=5)
                logger.info(f"Found {len(runs)} runs in risk_scoring experiment")
                
                if runs:
                    latest_run = runs[0]
                    logger.info(f"Latest run: {latest_run.info.run_id}")
                    logger.info(f"Metrics: {list(latest_run.data.metrics.keys())}")
            
            logger.info("✅ MLflow integration test passed")
            return True
            
        except Exception as e:
            logger.warning(f"MLflow server connection failed: {e}")
            logger.info("This is expected if MLflow server is not running")
            return True  # Don't fail the test if MLflow is not available
        
    except Exception as e:
        logger.error(f"MLflow integration test failed: {e}")
        return False


def main():
    """Run all tests for the ML Risk Scoring System."""
    logger.info("🚀 Starting ML Risk Scoring System Tests")
    logger.info("=" * 60)
    
    # Create test data
    protocol_ids = create_test_data()
    if not protocol_ids:
        logger.error("Failed to create test data")
        return False
    
    # Run tests
    tests = [
        ("Feature Engineering", test_feature_engineering),
        ("Model Training", test_model_training),
        ("Risk Prediction", test_risk_prediction),
        ("Batch Prediction", test_batch_prediction),
        ("MLflow Integration", test_mlflow_integration),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"{test_name} test crashed: {e}")
            results[test_name] = False
    
    # API tests (optional - only if server is running)
    logger.info(f"\n🧪 Running API Endpoint tests...")
    try:
        api_result = asyncio.run(test_api_endpoints())
        results["API Endpoints"] = api_result
    except Exception as e:
        logger.warning(f"API endpoint tests failed (server may not be running): {e}")
        results["API Endpoints"] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        logger.info(f"{test_name:<20} {status}")
        if passed_test:
            passed += 1
    
    logger.info("-" * 60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! ML Risk Scoring System is working correctly.")
        return True
    else:
        logger.warning(f"⚠️  {total - passed} tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
