"""
Advanced Anomaly Detection System for DeFi Protocols.

Tests multiple anomaly detection algorithms:
1. Isolation Forest (ensemble-based)
2. Local Outlier Factor (density-based)
3. One-Class SVM (boundary-based)
4. DBSCAN (clustering-based)
5. Autoencoder (deep learning-based)

Automatically selects the best performing algorithm.
"""
import logging
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from pyod.models.auto_encoder import AutoEncoder
from pyod.models.hbos import HBOS
from pyod.models.knn import KNN as PyOD_KNN
import joblib

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Anomaly detection result."""
    is_anomaly: bool
    anomaly_score: float  # 0-1, higher = more anomalous
    algorithm_used: str
    confidence: float
    details: Dict[str, Any]


@dataclass
class AlgorithmPerformance:
    """Performance metrics for an anomaly detection algorithm."""
    algorithm_name: str
    n_anomalies_detected: int
    anomaly_ratio: float
    silhouette_score: float
    mean_anomaly_score: float
    execution_time_ms: float


class AnomalyDetector:
    """
    Multi-algorithm anomaly detection system.
    
    Automatically tests and selects the best algorithm based on:
    - Silhouette score
    - Anomaly detection rate
    - Execution time
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers (0.0-0.5)
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.best_detector = None
        self.best_algorithm_name = ""
        self.algorithms_performance: List[AlgorithmPerformance] = []
        
        # Initialize algorithms
        self.algorithms = {
            'isolation_forest': IsolationForest(
                contamination=contamination,
                n_estimators=150,
                max_samples='auto',
                random_state=42,
                n_jobs=-1
            ),
            'local_outlier_factor': LocalOutlierFactor(
                contamination=contamination,
                n_neighbors=20,
                novelty=True,  # Allow predict on new data
                n_jobs=-1
            ),
            'one_class_svm': OneClassSVM(
                nu=contamination,
                kernel='rbf',
                gamma='scale'
            ),
            'hbos': HBOS(contamination=contamination),
            'knn_pyod': PyOD_KNN(
                contamination=contamination,
                n_neighbors=20,
                method='largest'
            )
        }
        
        logger.info(f"AnomalyDetector initialized with {len(self.algorithms)} algorithms")
    
    def fit(self, X: pd.DataFrame) -> Dict[str, AlgorithmPerformance]:
        """
        Train all anomaly detection algorithms and select the best.
        
        Args:
            X: Feature matrix (normal data)
        
        Returns:
            Dictionary of algorithm performances
        """
        import time
        
        logger.info(f"Training {len(self.algorithms)} anomaly detectors on {len(X)} samples...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        performances = {}
        best_score = -float('inf')
        
        for name, detector in self.algorithms.items():
            try:
                start_time = time.time()
                
                logger.info(f"Training {name}...")
                
                # Fit detector
                detector.fit(X_scaled)
                
                # Get predictions
                if hasattr(detector, 'predict'):
                    predictions = detector.predict(X_scaled)
                else:
                    # For LOF without novelty
                    predictions = detector.fit_predict(X_scaled)
                
                # Get anomaly scores
                if hasattr(detector, 'decision_function'):
                    scores = detector.decision_function(X_scaled)
                elif hasattr(detector, 'score_samples'):
                    scores = detector.score_samples(X_scaled)
                elif hasattr(detector, 'decision_scores_'):
                    scores = detector.decision_scores_
                else:
                    scores = np.zeros(len(X_scaled))
                
                # Normalize scores to 0-1
                if len(scores) > 0:
                    scores_normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-8)
                else:
                    scores_normalized = scores
                
                # Count anomalies (predictions = -1 for anomalies in sklearn)
                anomalies = (predictions == -1) if hasattr(detector, 'predict') else (predictions == 1)
                n_anomalies = int(anomalies.sum())
                anomaly_ratio = n_anomalies / len(X_scaled)
                
                # Calculate silhouette score (if enough anomalies)
                if n_anomalies > 1 and n_anomalies < len(X_scaled) - 1:
                    try:
                        sil_score = silhouette_score(X_scaled, predictions)
                    except:
                        sil_score = 0.0
                else:
                    sil_score = 0.0
                
                execution_time = (time.time() - start_time) * 1000  # milliseconds
                
                # Create performance record
                perf = AlgorithmPerformance(
                    algorithm_name=name,
                    n_anomalies_detected=n_anomalies,
                    anomaly_ratio=anomaly_ratio,
                    silhouette_score=sil_score,
                    mean_anomaly_score=float(scores_normalized.mean()),
                    execution_time_ms=execution_time
                )
                
                performances[name] = perf
                self.algorithms_performance.append(perf)
                
                logger.info(
                    f"{name}: {n_anomalies} anomalies ({anomaly_ratio:.1%}), "
                    f"Silhouette={sil_score:.3f}, Time={execution_time:.1f}ms"
                )
                
                # Select best based on composite score
                # Higher silhouette + reasonable anomaly ratio + fast execution
                composite_score = (
                    sil_score * 0.5 +
                    (1 - abs(anomaly_ratio - self.contamination)) * 0.3 +
                    (1 - min(execution_time / 1000, 1)) * 0.2
                )
                
                if composite_score > best_score:
                    best_score = composite_score
                    self.best_detector = detector
                    self.best_algorithm_name = name
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        if self.best_detector is None:
            # Fallback to Isolation Forest
            logger.warning("All detectors failed, using Isolation Forest as fallback")
            self.best_detector = IsolationForest(contamination=self.contamination, random_state=42)
            self.best_detector.fit(X_scaled)
            self.best_algorithm_name = "isolation_forest_fallback"
        
        logger.info(f"✅ Best detector: {self.best_algorithm_name} (score={best_score:.3f})")
        
        return performances
    
    def predict(self, X: pd.DataFrame) -> AnomalyResult:
        """
        Detect if data point is an anomaly.
        
        Args:
            X: Feature vector (single row DataFrame)
        
        Returns:
            AnomalyResult object
        """
        if self.best_detector is None:
            raise RuntimeError("Detector not trained. Call fit() first.")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get prediction
        prediction = self.best_detector.predict(X_scaled)[0]
        is_anomaly = (prediction == -1)
        
        # Get anomaly score
        if hasattr(self.best_detector, 'decision_function'):
            score = self.best_detector.decision_function(X_scaled)[0]
        elif hasattr(self.best_detector, 'score_samples'):
            score = self.best_detector.score_samples(X_scaled)[0]
        else:
            score = 0.0
        
        # Normalize score to 0-1 (higher = more anomalous)
        # For sklearn, negative scores indicate anomalies
        anomaly_score = float(1 / (1 + np.exp(score)))  # Sigmoid transformation
        
        # Confidence based on how far from decision boundary
        confidence = float(abs(score) / (abs(score) + 1))
        
        return AnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            algorithm_used=self.best_algorithm_name,
            confidence=confidence,
            details={
                'raw_score': float(score),
                'prediction': int(prediction),
                'threshold': 0.0
            }
        )
    
    def predict_batch(self, X: pd.DataFrame) -> List[AnomalyResult]:
        """Predict anomalies for multiple data points."""
        results = []
        for idx in range(len(X)):
            result = self.predict(X.iloc[[idx]])
            results.append(result)
        return results
    
    def get_best_detector_performance(self) -> Optional[AlgorithmPerformance]:
        """Get performance metrics for the best detector."""
        for perf in self.algorithms_performance:
            if perf.algorithm_name == self.best_algorithm_name:
                return perf
        return None
    
    def save(self, filepath: str) -> None:
        """Save trained detector."""
        joblib.dump({
            'detector': self.best_detector,
            'scaler': self.scaler,
            'algorithm_name': self.best_algorithm_name,
            'contamination': self.contamination,
            'performances': self.algorithms_performance
        }, filepath)
        logger.info(f"Anomaly detector saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load trained detector."""
        data = joblib.load(filepath)
        self.best_detector = data['detector']
        self.scaler = data['scaler']
        self.best_algorithm_name = data['algorithm_name']
        self.contamination = data['contamination']
        self.algorithms_performance = data.get('performances', [])
        logger.info(f"Anomaly detector loaded from {filepath}: {self.best_algorithm_name}")











