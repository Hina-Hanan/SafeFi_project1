"""
Phase 1 Testing Script - ML Infrastructure Components.

Tests:
1. Rate Limiter functionality
2. ML Risk Scorer (4 classification models)
3. Anomaly Detector (5 algorithms)
4. Feature importance extraction
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Import our components
from app.services.rate_limiter import RateLimiter, get_coingecko_rate_limiter
from app.services.ml_risk_scorer import MLRiskScorer, RiskPrediction
from app.services.anomaly_detector import AnomalyDetector, AnomalyResult


def print_header(title: str):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_rate_limiter():
    """Test the smart rate limiter."""
    print_header("TEST 1: Rate Limiter")
    
    try:
        # Create rate limiter (5 calls per 10 seconds for testing)
        limiter = RateLimiter(max_calls=5, period_seconds=10)
        logger.info("✅ RateLimiter created successfully")
        
        # Test async acquire
        async def test_acquire():
            logger.info("Testing rate limit acquisition...")
            for i in range(7):  # Try 7 calls (should wait after 5)
                await limiter.acquire()
                logger.info(f"  Call {i+1} acquired")
        
        # Run async test
        asyncio.run(test_acquire())
        
        # Get stats
        stats = limiter.get_stats()
        logger.info(f"✅ Rate Limiter Stats: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Rate Limiter test failed: {e}")
        return False


def test_ml_risk_scorer():
    """Test ML risk scoring with multiple models."""
    print_header("TEST 2: ML Risk Scorer (4 Models)")
    
    try:
        # Create sample data
        np.random.seed(42)
        n_samples = 200
        
        # Generate features (simulate protocol metrics)
        X = pd.DataFrame({
            'tvl_vol_30': np.random.uniform(0, 1, n_samples),
            'price_vol_30': np.random.uniform(0, 1, n_samples),
            'tvl_slope': np.random.uniform(-0.5, 0.5, n_samples),
            'liquidity_ratio': np.random.uniform(0, 1, n_samples),
            'drawdown_risk': np.random.uniform(0, 1, n_samples),
            'market_cap_stability': np.random.uniform(0, 1, n_samples),
        })
        
        # Generate labels (risk levels based on simple rules)
        y = []
        for idx in range(n_samples):
            row = X.iloc[idx]
            # High risk if high volatility or high drawdown
            if row['tvl_vol_30'] > 0.7 or row['drawdown_risk'] > 0.7:
                y.append('high')
            # Low risk if stable and positive trend
            elif row['market_cap_stability'] > 0.6 and row['tvl_slope'] > 0:
                y.append('low')
            else:
                y.append('medium')
        
        y = pd.Series(y)
        
        logger.info(f"Generated {len(X)} samples with {len(X.columns)} features")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        # Initialize scorer
        scorer = MLRiskScorer(use_smote=True)
        logger.info("✅ MLRiskScorer initialized")
        
        # Train models
        logger.info("Training 4 classification models...")
        performances = scorer.train(X, y, cv_folds=3)
        
        # Print results
        logger.info("\n📊 Model Performance Results:")
        for name, perf in performances.items():
            logger.info(
                f"  {name:20s} | F1={perf.f1_score:.3f} | "
                f"Acc={perf.accuracy:.3f} | CV={perf.cv_mean:.3f}±{perf.cv_std:.3f}"
            )
        
        # Get best model
        best_perf = scorer.get_best_model_performance()
        logger.info(f"\n✅ Best Model: {scorer.best_model_name}")
        logger.info(f"   F1 Score: {best_perf.f1_score:.3f}")
        logger.info(f"   Accuracy: {best_perf.accuracy:.3f}")
        
        # Test prediction
        logger.info("\n🔮 Testing prediction on new sample...")
        test_sample = X.iloc[[0]]
        prediction = scorer.predict(test_sample, protocol_id="test-protocol")
        
        logger.info(f"  Risk Level: {prediction.risk_level}")
        logger.info(f"  Risk Score: {prediction.risk_score:.3f}")
        logger.info(f"  Confidence: {prediction.confidence:.3f}")
        logger.info(f"  Model Used: {prediction.model_name}")
        
        # Feature importance
        if best_perf.feature_importance:
            logger.info("\n🎯 Top 3 Most Important Features:")
            sorted_features = sorted(
                best_perf.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            for feat, importance in sorted_features:
                logger.info(f"  {feat:25s}: {importance:.3f}")
        
        # Save model
        model_path = "models/test_ml_model.joblib"
        os.makedirs("models", exist_ok=True)
        scorer.save(model_path)
        logger.info(f"\n✅ Model saved to {model_path}")
        
        # Load model
        scorer2 = MLRiskScorer()
        scorer2.load(model_path)
        logger.info(f"✅ Model loaded successfully: {scorer2.best_model_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ML Risk Scorer test failed: {e}", exc_info=True)
        return False


def test_anomaly_detector():
    """Test anomaly detection with multiple algorithms."""
    print_header("TEST 3: Anomaly Detector (5 Algorithms)")
    
    try:
        # Create sample data with some anomalies
        np.random.seed(42)
        n_normal = 180
        n_anomalies = 20
        
        # Normal data (clustered around 0.5)
        normal_data = np.random.normal(0.5, 0.1, (n_normal, 6))
        
        # Anomalous data (extreme values)
        anomaly_data = np.random.uniform(0, 1, (n_anomalies, 6))
        anomaly_data = np.where(anomaly_data > 0.5, anomaly_data * 1.5, anomaly_data * 0.5)
        
        # Combine
        X = np.vstack([normal_data, anomaly_data])
        X = pd.DataFrame(
            X,
            columns=[
                'tvl_vol_30', 'price_vol_30', 'tvl_slope',
                'liquidity_ratio', 'drawdown_risk', 'market_cap_stability'
            ]
        )
        
        logger.info(f"Generated {len(X)} samples ({n_normal} normal, {n_anomalies} anomalies)")
        
        # Initialize detector
        detector = AnomalyDetector(contamination=0.1)
        logger.info("✅ AnomalyDetector initialized")
        
        # Train detectors
        logger.info("Training 5 anomaly detection algorithms...")
        performances = detector.fit(X)
        
        # Print results
        logger.info("\n📊 Anomaly Detection Results:")
        for name, perf in performances.items():
            logger.info(
                f"  {name:25s} | Anomalies={perf.n_anomalies_detected:3d} "
                f"({perf.anomaly_ratio:.1%}) | Silhouette={perf.silhouette_score:.3f} | "
                f"Time={perf.execution_time_ms:.1f}ms"
            )
        
        # Get best detector
        best_perf = detector.get_best_detector_performance()
        logger.info(f"\n✅ Best Detector: {detector.best_algorithm_name}")
        logger.info(f"   Anomalies Detected: {best_perf.n_anomalies_detected}")
        logger.info(f"   Silhouette Score: {best_perf.silhouette_score:.3f}")
        
        # Test prediction
        logger.info("\n🔍 Testing anomaly detection on new samples...")
        
        # Test normal sample
        normal_sample = X.iloc[[0]]
        result = detector.predict(normal_sample)
        logger.info(f"  Normal Sample: is_anomaly={result.is_anomaly}, "
                   f"score={result.anomaly_score:.3f}, confidence={result.confidence:.3f}")
        
        # Test anomalous sample
        anomaly_sample = X.iloc[[n_normal + 1]]
        result = detector.predict(anomaly_sample)
        logger.info(f"  Anomaly Sample: is_anomaly={result.is_anomaly}, "
                   f"score={result.anomaly_score:.3f}, confidence={result.confidence:.3f}")
        
        # Save detector
        detector_path = "models/test_anomaly_detector.joblib"
        detector.save(detector_path)
        logger.info(f"\n✅ Detector saved to {detector_path}")
        
        # Load detector
        detector2 = AnomalyDetector()
        detector2.load(detector_path)
        logger.info(f"✅ Detector loaded successfully: {detector2.best_algorithm_name}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Anomaly Detector test failed: {e}", exc_info=True)
        return False


def main():
    """Run all Phase 1 tests."""
    print("\n" + "🚀" * 40)
    print("  PHASE 1 TESTING - ML Infrastructure Components")
    print("🚀" * 40)
    print(f"\nTimestamp: {datetime.now()}")
    print(f"Python: {sys.version}")
    
    results = {
        'rate_limiter': False,
        'ml_risk_scorer': False,
        'anomaly_detector': False
    }
    
    # Test 1: Rate Limiter
    results['rate_limiter'] = test_rate_limiter()
    
    # Test 2: ML Risk Scorer
    results['ml_risk_scorer'] = test_ml_risk_scorer()
    
    # Test 3: Anomaly Detector
    results['anomaly_detector'] = test_anomaly_detector()
    
    # Summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:25s}: {status}")
    
    print(f"\n{'='*80}")
    print(f"  TOTAL: {passed_tests}/{total_tests} tests passed")
    print(f"{'='*80}\n")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Phase 1 is ready for Phase 2 integration.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)











