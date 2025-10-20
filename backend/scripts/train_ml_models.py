"""
ML Model Training Pipeline.

This script:
1. Collects historical data from the database
2. Engineers features for risk prediction and anomaly detection
3. Trains ML classification models (RandomForest, XGBoost, LightGBM, CatBoost)
4. Trains anomaly detection models (Isolation Forest, LOF, One-Class SVM, etc.)
5. Evaluates and saves the best models
6. Logs metrics and feature importance

Usage:
    python scripts/train_ml_models.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Protocol, ProtocolMetric, RiskScore
from app.services.ml_risk_scorer import MLRiskScorer
from app.services.anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ml_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create directories
os.makedirs('models', exist_ok=True)
os.makedirs('logs', exist_ok=True)


def collect_training_data(db: Session, days: int = 90) -> pd.DataFrame:
    """
    Collect historical protocol data for training.
    
    Args:
        db: Database session
        days: Number of days of history to collect
        
    Returns:
        DataFrame with protocol features and labels
    """
    logger.info(f"Collecting training data from last {days} days...")
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get all active protocols
    protocols = db.query(Protocol).filter(Protocol.is_active == True).all()
    logger.info(f"Found {len(protocols)} active protocols")
    
    training_data = []
    
    for protocol in protocols:
        # Get metrics for this protocol
        metrics = (
            db.query(ProtocolMetric)
            .filter(
                ProtocolMetric.protocol_id == protocol.id,
                ProtocolMetric.timestamp >= cutoff_date
            )
            .order_by(ProtocolMetric.timestamp.desc())
            .all()
        )
        
        if len(metrics) < 10:  # Need at least 10 data points
            logger.warning(f"Skipping {protocol.name}: insufficient data ({len(metrics)} points)")
            continue
        
        # Get risk scores
        risk_scores = (
            db.query(RiskScore)
            .filter(
                RiskScore.protocol_id == protocol.id,
                RiskScore.timestamp >= cutoff_date
            )
            .order_by(RiskScore.timestamp.desc())
            .all()
        )
        
        # Convert to DataFrame for easier feature engineering
        metrics_df = pd.DataFrame([{
            'timestamp': m.timestamp,
            'tvl': float(m.tvl) if m.tvl else 0,
            'volume_24h': float(m.volume_24h) if m.volume_24h else 0,
            'price': float(m.price) if m.price else 0,
            'market_cap': float(m.market_cap) if m.market_cap else 0,
            'price_change_24h': float(m.price_change_24h) if m.price_change_24h else 0,
        } for m in metrics])
        
        if len(metrics_df) > 0:
            # Engineer features
            features = engineer_features(protocol, metrics_df)
            
            # Add label (use latest risk score if available)
            if risk_scores:
                latest_risk = risk_scores[0]
                features['risk_level'] = latest_risk.risk_level
            else:
                # Create heuristic label based on volatility and trends
                features['risk_level'] = create_heuristic_label(features)
            
            features['protocol_id'] = protocol.id
            features['protocol_name'] = protocol.name
            training_data.append(features)
    
    df = pd.DataFrame(training_data)
    logger.info(f"Collected {len(df)} training samples")
    logger.info(f"Class distribution: {df['risk_level'].value_counts().to_dict()}")
    
    return df


def engineer_features(protocol: Protocol, metrics_df: pd.DataFrame) -> dict:
    """
    Engineer features from raw protocol metrics.
    
    Returns:
        Dictionary of engineered features
    """
    features = {}
    
    # Volatility features (30-day rolling)
    if len(metrics_df) >= 30:
        features['tvl_vol_30'] = metrics_df['tvl'].tail(30).std() / (metrics_df['tvl'].tail(30).mean() + 1e-10)
        features['price_vol_30'] = metrics_df['price'].tail(30).std() / (metrics_df['price'].tail(30).mean() + 1e-10)
        features['volume_vol_30'] = metrics_df['volume_24h'].tail(30).std() / (metrics_df['volume_24h'].tail(30).mean() + 1e-10)
    else:
        features['tvl_vol_30'] = metrics_df['tvl'].std() / (metrics_df['tvl'].mean() + 1e-10)
        features['price_vol_30'] = metrics_df['price'].std() / (metrics_df['price'].mean() + 1e-10)
        features['volume_vol_30'] = metrics_df['volume_24h'].std() / (metrics_df['volume_24h'].mean() + 1e-10)
    
    # Trend features
    features['tvl_slope'] = calculate_slope(metrics_df['tvl'].values)
    features['price_slope'] = calculate_slope(metrics_df['price'].values)
    features['volume_slope'] = calculate_slope(metrics_df['volume_24h'].values)
    
    # Liquidity features
    latest = metrics_df.iloc[0]
    features['liquidity_ratio'] = latest['volume_24h'] / (latest['tvl'] + 1e-10)
    features['market_cap_to_tvl'] = latest['market_cap'] / (latest['tvl'] + 1e-10)
    
    # Drawdown features
    features['max_drawdown'] = calculate_max_drawdown(metrics_df['price'].values)
    features['tvl_max_drawdown'] = calculate_max_drawdown(metrics_df['tvl'].values)
    
    # Stability features
    features['price_change_abs_mean'] = metrics_df['price_change_24h'].abs().mean()
    features['price_change_std'] = metrics_df['price_change_24h'].std()
    
    # Protocol metadata features
    features['protocol_category'] = encode_category(protocol.category)
    features['protocol_chain'] = encode_chain(protocol.chain)
    
    # Recent performance
    features['recent_price_change'] = latest['price_change_24h']
    features['recent_tvl'] = np.log1p(latest['tvl'])  # Log scale for better distribution
    features['recent_volume'] = np.log1p(latest['volume_24h'])
    
    return features


def calculate_slope(values: np.ndarray) -> float:
    """Calculate linear regression slope of time series."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values))
    slope, _ = np.polyfit(x, values, 1)
    return float(slope)


def calculate_max_drawdown(prices: np.ndarray) -> float:
    """Calculate maximum drawdown from peak."""
    if len(prices) < 2:
        return 0.0
    cummax = np.maximum.accumulate(prices)
    drawdown = (prices - cummax) / (cummax + 1e-10)
    return float(np.min(drawdown))


def encode_category(category: str) -> int:
    """Encode protocol category as integer."""
    categories = {
        'dex': 0, 'lending': 1, 'yield': 2, 'derivatives': 3,
        'staking': 4, 'bridge': 5, 'other': 6
    }
    return categories.get(category.lower() if category else 'other', 6)


def encode_chain(chain: str) -> int:
    """Encode blockchain as integer."""
    chains = {
        'ethereum': 0, 'bsc': 1, 'polygon': 2, 'avalanche': 3,
        'arbitrum': 4, 'optimism': 5, 'solana': 6, 'other': 7
    }
    return chains.get(chain.lower() if chain else 'other', 7)


def create_heuristic_label(features: dict) -> str:
    """
    Create heuristic risk label based on features.
    
    This is used when historical risk scores are not available.
    """
    # High risk criteria
    high_risk_score = 0
    
    if features.get('tvl_vol_30', 0) > 0.3:
        high_risk_score += 1
    if features.get('price_vol_30', 0) > 0.3:
        high_risk_score += 1
    if features.get('max_drawdown', 0) < -0.3:
        high_risk_score += 1
    if features.get('liquidity_ratio', 0) < 0.1:
        high_risk_score += 1
    
    # Low risk criteria
    low_risk_score = 0
    
    if features.get('tvl_slope', 0) > 0:
        low_risk_score += 1
    if features.get('price_vol_30', 0) < 0.1:
        low_risk_score += 1
    if features.get('liquidity_ratio', 0) > 0.5:
        low_risk_score += 1
    
    if high_risk_score >= 2:
        return 'high'
    elif low_risk_score >= 2:
        return 'low'
    else:
        return 'medium'


def train_risk_scoring_models(df: pd.DataFrame) -> MLRiskScorer:
    """
    Train risk scoring classification models.
    
    Returns:
        Trained MLRiskScorer
    """
    logger.info("=" * 80)
    logger.info("TRAINING RISK SCORING MODELS")
    logger.info("=" * 80)
    
    # Prepare features and labels
    feature_columns = [
        'tvl_vol_30', 'price_vol_30', 'volume_vol_30',
        'tvl_slope', 'price_slope', 'volume_slope',
        'liquidity_ratio', 'market_cap_to_tvl',
        'max_drawdown', 'tvl_max_drawdown',
        'price_change_abs_mean', 'price_change_std',
        'protocol_category', 'protocol_chain',
        'recent_price_change', 'recent_tvl', 'recent_volume'
    ]
    
    X = df[feature_columns]
    y = df['risk_level']
    
    logger.info(f"Training data shape: {X.shape}")
    logger.info(f"Features: {list(X.columns)}")
    
    # Initialize and train
    scorer = MLRiskScorer(use_smote=True)
    performances = scorer.train(X, y, cv_folds=5)
    
    # Log results
    logger.info("\n" + "=" * 80)
    logger.info("RISK SCORING MODEL PERFORMANCE")
    logger.info("=" * 80)
    
    for model_name, perf in performances.items():
        logger.info(
            f"{model_name:20s} | "
            f"F1={perf.f1_score:.4f} | "
            f"Accuracy={perf.accuracy:.4f} | "
            f"Precision={perf.precision:.4f} | "
            f"Recall={perf.recall:.4f} | "
            f"CV={perf.cv_mean:.4f}±{perf.cv_std:.4f}"
        )
    
    best_perf = scorer.get_best_model_performance()
    logger.info(f"\nBest Model: {scorer.best_model_name}")
    logger.info(f"F1 Score: {best_perf.f1_score:.4f}")
    
    # Log feature importance
    if best_perf.feature_importance:
        logger.info("\nTop 10 Most Important Features:")
        sorted_features = sorted(
            best_perf.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        for i, (feat, importance) in enumerate(sorted_features, 1):
            logger.info(f"{i:2d}. {feat:30s}: {importance:.4f}")
    
    # Save model
    model_path = 'models/ml_risk_scorer.joblib'
    scorer.save(model_path)
    logger.info(f"\nModel saved to: {model_path}")
    
    return scorer


def train_anomaly_detection_models(df: pd.DataFrame) -> AnomalyDetector:
    """
    Train anomaly detection models.
    
    Returns:
        Trained AnomalyDetector
    """
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING ANOMALY DETECTION MODELS")
    logger.info("=" * 80)
    
    # Use same features as risk scoring
    feature_columns = [
        'tvl_vol_30', 'price_vol_30', 'volume_vol_30',
        'tvl_slope', 'price_slope', 'volume_slope',
        'liquidity_ratio', 'market_cap_to_tvl',
        'max_drawdown', 'tvl_max_drawdown',
        'price_change_abs_mean', 'price_change_std',
        'recent_price_change', 'recent_tvl', 'recent_volume'
    ]
    
    X = df[feature_columns]
    
    logger.info(f"Training data shape: {X.shape}")
    
    # Initialize and train
    detector = AnomalyDetector(contamination=0.1)  # Expect ~10% anomalies
    performances = detector.fit(X)
    
    # Log results
    logger.info("\n" + "=" * 80)
    logger.info("ANOMALY DETECTION MODEL PERFORMANCE")
    logger.info("=" * 80)
    
    for algo_name, perf in performances.items():
        logger.info(
            f"{algo_name:30s} | "
            f"Anomalies={perf.n_anomalies_detected:4d} ({perf.anomaly_ratio:.2%}) | "
            f"Silhouette={perf.silhouette_score:.4f} | "
            f"Time={perf.execution_time_ms:.1f}ms"
        )
    
    best_perf = detector.get_best_detector_performance()
    logger.info(f"\nBest Algorithm: {detector.best_algorithm_name}")
    logger.info(f"Anomalies Detected: {best_perf.n_anomalies_detected}")
    logger.info(f"Silhouette Score: {best_perf.silhouette_score:.4f}")
    
    # Save detector
    detector_path = 'models/anomaly_detector.joblib'
    detector.save(detector_path)
    logger.info(f"\nDetector saved to: {detector_path}")
    
    return detector


def main():
    """Main training pipeline."""
    logger.info("\n" + "🚀" * 40)
    logger.info("ML MODEL TRAINING PIPELINE")
    logger.info("🚀" * 40)
    logger.info(f"\nStarted at: {datetime.now()}")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Collect training data
        df = collect_training_data(db, days=90)
        
        if len(df) < 20:
            logger.error(f"Insufficient training data: {len(df)} samples (minimum 20 required)")
            logger.error("Please run data collection first: python scripts/collect_live_data.py")
            return 1
        
        # Train risk scoring models
        risk_scorer = train_risk_scoring_models(df)
        
        # Train anomaly detection models
        anomaly_detector = train_anomaly_detection_models(df)
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ TRAINING COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Risk Scoring Model: {risk_scorer.best_model_name}")
        logger.info(f"Anomaly Detector: {anomaly_detector.best_algorithm_name}")
        logger.info(f"Completed at: {datetime.now()}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)




