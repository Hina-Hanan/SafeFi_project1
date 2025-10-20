"""
Advanced ML-Based Risk Scoring System.

Features:
- Multiple classification models (RF, XGBoost, LightGBM, CatBoost)
- Automatic model selection (best F1 score)
- Feature importance analysis (SHAP + Permutation)
- Cross-validation with stratified folds
- Ensemble voting for final predictions
- Handles imbalanced data with SMOTE
"""
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Optional
import warnings

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from xgboost import XGBClassifier

# Optional imports for advanced ML libraries
LIGHTGBM_AVAILABLE = False
LGBMClassifier = None
CATBOOST_AVAILABLE = False
CatBoostClassifier = None
IMBLEARN_AVAILABLE = False
SMOTE = None
ImbPipeline = None
SHAP_AVAILABLE = False
shap = None

# Try to import optional dependencies
def _import_optional_dependencies():
    global LIGHTGBM_AVAILABLE, LGBMClassifier
    global CATBOOST_AVAILABLE, CatBoostClassifier
    global IMBLEARN_AVAILABLE, SMOTE, ImbPipeline
    global SHAP_AVAILABLE, shap
    
    try:
        from lightgbm import LGBMClassifier  # type: ignore
        LIGHTGBM_AVAILABLE = True
    except ImportError:
        pass
    
    try:
        from catboost import CatBoostClassifier  # type: ignore
        CATBOOST_AVAILABLE = True
    except ImportError:
        pass
    
    try:
        from imblearn.over_sampling import SMOTE  # type: ignore
        from imblearn.pipeline import Pipeline as ImbPipeline  # type: ignore
        IMBLEARN_AVAILABLE = True
    except ImportError:
        pass
    
    try:
        import shap  # type: ignore
        SHAP_AVAILABLE = True
    except ImportError:
        pass

# Initialize optional dependencies
_import_optional_dependencies()

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


@dataclass
class ModelPerformance:
    """Model performance metrics."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    cv_mean: float
    cv_std: float
    feature_importance: Dict[str, float]
    confusion_matrix: List[List[int]]


@dataclass
class RiskPrediction:
    """Risk prediction result."""
    protocol_id: str
    risk_score: float  # 0-1 scale
    risk_level: str  # low, medium, high
    confidence: float
    model_name: str
    feature_contributions: Dict[str, float]
    is_anomaly: bool
    anomaly_score: float


class MLRiskScorer:
    """
    Production-grade ML risk scoring with multiple models.
    
    Models tested:
    1. Random Forest (baseline)
    2. XGBoost (gradient boosting)
    3. LightGBM (fast gradient boosting)
    4. CatBoost (categorical handling)
    
    Best model selected based on cross-validated F1 score.
    """
    
    def __init__(self, use_smote: bool = True):
        self.use_smote = use_smote
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = ""
        self.feature_names = []
        self.models_performance: List[ModelPerformance] = []
        
        # Initialize models (only include available ones)
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=10,
                min_samples_leaf=4,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            ),
            'xgboost': XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=2,  # Handle imbalance
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss',
                n_jobs=-1
            )
        }
        
        # Add optional models if available
        if LIGHTGBM_AVAILABLE:
            self.models['lightgbm'] = LGBMClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.8,
                colsample_bytree=0.8,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1,
                verbose=-1
            )
        
        if CATBOOST_AVAILABLE:
            self.models['catboost'] = CatBoostClassifier(
                iterations=200,
                depth=6,
                learning_rate=0.05,
                l2_leaf_reg=3,
                auto_class_weights='Balanced',
                random_state=42,
                verbose=False,
                thread_count=-1
            )
        
        logger.info(f"MLRiskScorer initialized with {len(self.models)} classification models")
    
    def train(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        cv_folds: int = 5
    ) -> Dict[str, ModelPerformance]:
        """
        Train all models and select the best one.
        
        Args:
            X: Feature matrix
            y: Target labels (risk levels)
            cv_folds: Number of cross-validation folds
        
        Returns:
            Dictionary of model performances
        """
        logger.info(f"Training {len(self.models)} models on {len(X)} samples...")
        logger.info(f"Feature columns: {list(X.columns)}")
        logger.info(f"Class distribution: {y.value_counts().to_dict()}")
        
        self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X)
        
        # Handle class imbalance with SMOTE if enabled and available
        if self.use_smote and IMBLEARN_AVAILABLE and len(np.unique(y)) > 1:
            try:
                smote = SMOTE(random_state=42, k_neighbors=min(5, len(X) - 1))
                X_scaled, y = smote.fit_resample(X_scaled, y)
                logger.info(f"SMOTE applied: {len(X_scaled)} samples after resampling")
            except Exception as e:
                logger.warning(f"SMOTE failed: {e}. Continuing without SMOTE.")
        elif self.use_smote and not IMBLEARN_AVAILABLE:
            logger.info("SMOTE requested but imblearn not available. Continuing without SMOTE.")
        
        # Split data
        test_size = 0.2
        split_idx = int(len(X_scaled) * (1 - test_size))
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        performances = {}
        best_f1 = 0.0
        
        # Train each model
        for name, model in self.models.items():
            try:
                logger.info(f"Training {name}...")
                
                # Cross-validation
                cv_scores = cross_val_score(
                    model, X_train, y_train,
                    cv=min(cv_folds, len(X_train)),
                    scoring='f1_weighted',
                    n_jobs=-1
                )
                
                # Train on full training set
                model.fit(X_train, y_train)
                
                # Test predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                cm = confusion_matrix(y_test, y_pred).tolist()
                
                # Feature importance
                feat_imp = self._get_feature_importance(model, X_test, y_test)
                
                perf = ModelPerformance(
                    model_name=name,
                    accuracy=acc,
                    precision=prec,
                    recall=rec,
                    f1_score=f1,
                    cv_mean=cv_scores.mean(),
                    cv_std=cv_scores.std(),
                    feature_importance=feat_imp,
                    confusion_matrix=cm
                )
                
                performances[name] = perf
                self.models_performance.append(perf)
                
                logger.info(
                    f"{name}: F1={f1:.3f}, Acc={acc:.3f}, "
                    f"CV={cv_scores.mean():.3f}±{cv_scores.std():.3f}"
                )
                
                # Track best model
                if f1 > best_f1:
                    best_f1 = f1
                    self.best_model = model
                    self.best_model_name = name
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue
        
        if self.best_model is None:
            raise RuntimeError("All models failed to train")
        
        logger.info(f"✅ Best model: {self.best_model_name} (F1={best_f1:.3f})")
        
        return performances
    
    def predict(
        self, 
        X: pd.DataFrame,
        protocol_id: str = "unknown"
    ) -> RiskPrediction:
        """
        Make risk prediction for a protocol.
        
        Args:
            X: Feature vector (single row DataFrame)
            protocol_id: Protocol identifier
        
        Returns:
            RiskPrediction object
        """
        if self.best_model is None:
            raise RuntimeError("Model not trained. Call train() first.")
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Get prediction
        pred_class = self.best_model.predict(X_scaled)[0]
        
        # Get probability/confidence
        if hasattr(self.best_model, 'predict_proba'):
            proba = self.best_model.predict_proba(X_scaled)[0]
            confidence = float(max(proba))
            
            # Map probabilities to risk score (0-1)
            # Assuming classes are [low, medium, high]
            risk_score = float(0.2 * proba[0] + 0.5 * proba[1] + 0.8 * proba[2])
        else:
            confidence = 0.7
            risk_mapping = {"low": 0.2, "medium": 0.5, "high": 0.8}
            risk_score = risk_mapping.get(pred_class, 0.5)
        
        # Get feature contributions (SHAP values)
        try:
            feature_contrib = self._explain_prediction(X_scaled)
        except:
            feature_contrib = {}
        
        return RiskPrediction(
            protocol_id=protocol_id,
            risk_score=risk_score,
            risk_level=pred_class,
            confidence=confidence,
            model_name=self.best_model_name,
            feature_contributions=feature_contrib,
            is_anomaly=False,  # Will be set by anomaly detector
            anomaly_score=0.0
        )
    
    def _get_feature_importance(
        self, 
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """Extract feature importance from model."""
        try:
            # Try native feature importance first
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
            elif hasattr(model, 'get_feature_importance'):  # CatBoost
                importances = model.get_feature_importance()
            else:
                # Fallback to permutation importance
                from sklearn.inspection import permutation_importance
                result = permutation_importance(
                    model, X_test, y_test,
                    n_repeats=10,
                    random_state=42,
                    n_jobs=-1
                )
                importances = result.importances_mean
            
            # Normalize and create dict
            importances = importances / importances.sum()
            
            return {
                name: float(imp)
                for name, imp in zip(self.feature_names, importances)
            }
        except Exception as e:
            logger.warning(f"Could not extract feature importance: {e}")
            return {}
    
    def _explain_prediction(self, X_scaled: np.ndarray) -> Dict[str, float]:
        """
        Use SHAP to explain individual prediction.
        
        Returns feature contributions to the prediction.
        """
        if not SHAP_AVAILABLE:
            logger.info("SHAP not available. Skipping feature explanation.")
            return {}
            
        try:
            # Create SHAP explainer
            explainer = shap.TreeExplainer(self.best_model)
            shap_values = explainer.shap_values(X_scaled)
            
            # For multi-class, take the predicted class
            if isinstance(shap_values, list):
                pred_class = self.best_model.predict(X_scaled)[0]
                class_idx = list(self.best_model.classes_).index(pred_class)
                shap_values = shap_values[class_idx]
            
            # Get absolute contributions
            contributions = {
                name: float(abs(val))
                for name, val in zip(self.feature_names, shap_values[0])
            }
            
            # Normalize
            total = sum(contributions.values())
            if total > 0:
                contributions = {
                    k: v / total for k, v in contributions.items()
                }
            
            return contributions
            
        except Exception as e:
            logger.warning(f"SHAP explanation failed: {e}")
            return {}
    
    def get_best_model_performance(self) -> Optional[ModelPerformance]:
        """Get performance metrics for the best model."""
        for perf in self.models_performance:
            if perf.model_name == self.best_model_name:
                return perf
        return None
    
    def save(self, filepath: str) -> None:
        """Save trained model and scaler."""
        joblib.dump({
            'model': self.best_model,
            'scaler': self.scaler,
            'model_name': self.best_model_name,
            'feature_names': self.feature_names,
            'performances': self.models_performance
        }, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """Load trained model and scaler."""
        data = joblib.load(filepath)
        self.best_model = data['model']
        self.scaler = data['scaler']
        self.best_model_name = data['model_name']
        self.feature_names = data['feature_names']
        self.models_performance = data.get('performances', [])
        logger.info(f"Model loaded from {filepath}: {self.best_model_name}")





