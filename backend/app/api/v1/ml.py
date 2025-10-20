from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.risk_calculator import RiskCalculatorService, ModelPerformance, RiskPrediction


router = APIRouter(prefix="/models", tags=["ml"])


class ModelPerformanceSchema(BaseModel):
    """Schema for model performance metrics."""
    model_config = {"protected_namespaces": ()}
    
    accuracy: float
    precision: float
    recall: float
    f1: float
    best_params: Dict[str, Any]
    model_name: str
    classification_report: str
    run_id: str
    model_uri: str


class TrainResponse(BaseModel):
    """Response schema for model training."""
    success: bool
    message: str
    models: List[ModelPerformanceSchema]
    best_model: str
    training_time: str


class ModelPerformanceResponse(BaseModel):
    """Comprehensive model performance response."""
    model_config = {"protected_namespaces": ()}
    
    experiment_name: str
    total_runs: int
    recent_runs: List[Dict[str, Any]]
    model_registry: Dict[str, Any]
    performance_summary: Dict[str, Any]


class ModelComparisonResponse(BaseModel):
    """Model version comparison response."""
    model_config = {"protected_namespaces": ()}
    
    model_name: str
    total_versions: int
    version_comparison: List[Dict[str, Any]]


@router.post("/train", response_model=TrainResponse)
def train_models() -> TrainResponse:
    """
    Train multiple ML models with comprehensive evaluation.
    
    Features:
    - RandomForest, XGBoost, and Logistic Regression
    - Hyperparameter tuning with cross-validation
    - MLflow experiment tracking and model registry
    - Feature engineering and preprocessing
    - Performance metrics and model comparison
    """
    service = RiskCalculatorService()
    try:
        import time
        start_time = time.time()
        
        performances = service.train_models()
        
        training_time = f"{time.time() - start_time:.2f} seconds"
        best_model = max(performances, key=lambda p: p.f1).model_name
        
        # Convert dataclass to dict for response
        model_schemas = []
        for perf in performances:
            model_schemas.append(ModelPerformanceSchema(
                accuracy=perf.accuracy,
                precision=perf.precision,
                recall=perf.recall,
                f1=perf.f1,
                best_params=perf.best_params,
                model_name=perf.model_name,
                classification_report=perf.classification_report,
                run_id=perf.run_id,
                model_uri=perf.model_uri
            ))
        
        return TrainResponse(
            success=True,
            message=f"Successfully trained {len(performances)} models",
            models=model_schemas,
            best_model=best_model,
            training_time=training_time
        )
        
    except Exception as exc:
        # Return friendly response without failing hard during validation
        return TrainResponse(
            success=False,
            message=f"Training skipped or failed: {str(exc)}",
            models=[],
            best_model="",
            training_time="0s"
        )


@router.get("/performance", response_model=ModelPerformanceResponse)
def get_model_performance() -> ModelPerformanceResponse:
    """
    Get comprehensive model performance metrics from MLflow.
    
    Returns:
    - Recent training runs and metrics
    - Model registry information
    - Performance trends and summaries
    """
    try:
        service = RiskCalculatorService()
        metrics = service.get_model_performance_metrics()
        if "error" in metrics:
            # Gracefully degrade
            return ModelPerformanceResponse(
                experiment_name="risk_scoring",
                total_runs=0,
                recent_runs=[],
                model_registry={},
                performance_summary={}
            )
        return ModelPerformanceResponse(**metrics)
    except Exception as e:
        # Gracefully degrade when MLflow is not available
        return ModelPerformanceResponse(
            experiment_name="risk_scoring",
            total_runs=0,
            recent_runs=[],
            model_registry={},
            performance_summary={}
        )


@router.get("/compare/{model_name}", response_model=ModelComparisonResponse)
def compare_model_versions(model_name: str) -> ModelComparisonResponse:
    """
    Compare different versions of a specific model.
    
    Args:
        model_name: Name of the model (e.g., 'risk_scoring_rf')
    
    Returns:
        Detailed comparison of all model versions
    """
    service = RiskCalculatorService()
    try:
        comparison = service.compare_model_versions(model_name)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return ModelComparisonResponse(**comparison)
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare model versions: {str(exc)}"
        )


risk_router = APIRouter(prefix="/ml/risk", tags=["ml-risk"])


class RiskPredictionSchema(BaseModel):
    """Comprehensive risk prediction response schema."""
    model_config = {"protected_namespaces": ()}
    
    protocol_id: str
    risk_score: float = Field(..., description="Risk score between 0 and 1")
    risk_level: str = Field(..., description="Risk level: low, medium, or high")
    confidence: float = Field(..., description="Prediction confidence score")
    features: Dict[str, float] = Field(..., description="Feature values used for prediction")
    model_version: str = Field(..., description="Version of the model used")
    explanation: Dict[str, Any] = Field(..., description="Detailed explanation of the prediction")
    timestamp: Optional[str] = Field(None, description="Prediction timestamp")


class BatchRiskRequest(BaseModel):
    """Request schema for batch risk calculation."""
    protocol_ids: Optional[List[str]] = Field(None, description="Specific protocol IDs to analyze")
    force_refresh: bool = Field(False, description="Force recalculation even if recent data exists")


class BatchRiskResponse(BaseModel):
    """Response schema for batch risk calculation."""
    success: bool
    message: str
    total_protocols: int
    successful_predictions: int
    failed_predictions: int
    results: List[RiskPredictionSchema]
    processing_time: str


@risk_router.get("/protocols/{protocol_id}/risk-details")
def get_protocol_risk_details(protocol_id: str):
    """
    Get detailed risk analysis for a specific protocol using REAL database data.
    
    Returns comprehensive risk assessment including:
    - Risk score and level classification from database
    - Volatility and liquidity scores from latest risk score
    - Feature importance and explanations
    - Model confidence and version information
    - Human-readable risk factor interpretations
    """
    from app.database.connection import get_db
    from app.database.models import RiskScore
    from datetime import datetime
    
    # Get the LATEST risk score from database (REAL data, not synthetic!)
    db = next(get_db())
    latest_risk = (
        db.query(RiskScore)
        .filter(RiskScore.protocol_id == protocol_id)
        .order_by(RiskScore.timestamp.desc())
        .first()
    )
    
    if not latest_risk:
        raise HTTPException(
            status_code=404,
            detail=f"No risk scores found for protocol {protocol_id}"
        )
    
    # Return REAL database data in frontend-compatible format
    return {
        "protocol_id": protocol_id,
        "risk_score": float(latest_risk.risk_score),
        "risk_level": latest_risk.risk_level,
        "confidence": 0.85,  # Default confidence for database scores
        "volatility_score": float(latest_risk.volatility_score) if latest_risk.volatility_score else None,
        "liquidity_score": float(latest_risk.liquidity_score) if latest_risk.liquidity_score else None,
        "model_version": latest_risk.model_version,
        "timestamp": latest_risk.timestamp.isoformat(),
        "features": {},  # Feature breakdown can be added later
        "explanation": {
            "method": "database_lookup",
            "data_source": "real_database",
            "last_calculated": latest_risk.timestamp.isoformat()
        }
    }


@risk_router.post("/calculate-batch", response_model=BatchRiskResponse)
def calculate_batch_risk(request: BatchRiskRequest) -> BatchRiskResponse:
    """
    Calculate risk scores for multiple protocols in batch.
    
    Features:
    - Processes all active protocols by default
    - Optional filtering by specific protocol IDs
    - Comprehensive error handling and reporting
    - Performance monitoring and MLflow logging
    - Database persistence of results
    """
    service = RiskCalculatorService()
    try:
        import time
        start_time = time.time()
        
        # TODO: Implement protocol_ids filtering if needed
        results = service.predict_batch()
        
        processing_time = f"{time.time() - start_time:.2f} seconds"
        
        # Convert dict results to schema objects
        risk_predictions = []
        failed_count = 0
        
        for result in results:
            try:
                risk_predictions.append(RiskPredictionSchema(
                    protocol_id=result["protocol_id"],
                    risk_score=result["risk_score"],
                    risk_level=result["risk_level"],
                    confidence=result["confidence"],
                    features=result["features"],
                    model_version=result["model_version"],
                    explanation=result["explanation"],
                    timestamp=result.get("timestamp")
                ))
            except Exception:
                failed_count += 1
                continue
        
        return BatchRiskResponse(
            success=True,
            message=f"Batch risk calculation completed",
            total_protocols=len(results) + failed_count,
            successful_predictions=len(risk_predictions),
            failed_predictions=failed_count,
            results=risk_predictions,
            processing_time=processing_time
        )
        
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Batch risk calculation failed: {str(exc)}"
        )


@risk_router.get("/protocols/{protocol_id}/history")
def get_protocol_risk_history(
    protocol_id: str,
    limit: int = Query(50, ge=1, le=200, description="Number of historical records to return"),
    days: int = Query(30, ge=1, le=365, description="Number of days of history to include")
) -> Dict[str, Any]:
    """
    Get historical risk scores for a protocol.
    
    Returns time series of risk assessments for trend analysis.
    """
    from app.database.connection import SessionLocal
    from app.database.models import RiskScore
    from datetime import datetime, timedelta
    from sqlalchemy import desc
    
    db = SessionLocal()
    try:
        # Query historical risk scores
        cutoff_date = datetime.now() - timedelta(days=days)
        
        risk_scores = db.query(RiskScore).filter(
            RiskScore.protocol_id == protocol_id,
            RiskScore.timestamp >= cutoff_date
        ).order_by(desc(RiskScore.timestamp)).limit(limit).all()
        
        if not risk_scores:
            raise HTTPException(
                status_code=404,
                detail=f"No risk history found for protocol {protocol_id}"
            )
        
        # Convert to response format
        history = []
        for score in risk_scores:
            history.append({
                "timestamp": score.timestamp.isoformat(),
                "risk_score": float(score.risk_score),
                "risk_level": score.risk_level,
                "volatility_score": float(score.volatility_score) if score.volatility_score else None,
                "liquidity_score": float(score.liquidity_score) if score.liquidity_score else None,
                "model_version": score.model_version
            })
        
        return {
            "protocol_id": protocol_id,
            "history": history,
            "total_records": len(history),
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve risk history: {str(exc)}"
        )
    finally:
        db.close()


# Anomaly Detection Endpoints
anomaly_router = APIRouter(prefix="/anomaly", tags=["anomaly-detection"])


@anomaly_router.get("/protocols/{protocol_id}")
def detect_protocol_anomaly(protocol_id: str) -> Dict[str, Any]:
    """
    Detect if a protocol exhibits anomalous behavior.
    
    Uses trained anomaly detection models to identify unusual patterns
    in protocol metrics that may indicate emerging risks.
    """
    import os
    from pathlib import Path
    
    detector_path = Path("models/anomaly_detector.joblib")
    
    if not detector_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Anomaly detector not trained. Please train models first."
        )
    
    try:
        from app.services.anomaly_detector import AnomalyDetector
        from app.database.connection import SessionLocal
        from app.database.models import Protocol, ProtocolMetric
        from datetime import datetime, timedelta
        import pandas as pd
        import numpy as np
        
        # Load trained detector
        detector = AnomalyDetector()
        detector.load(str(detector_path))
        
        # Get protocol data
        db = SessionLocal()
        try:
            protocol = db.query(Protocol).filter_by(id=protocol_id).first()
            if not protocol:
                raise HTTPException(
                    status_code=404,
                    detail=f"Protocol not found: {protocol_id}"
                )
            
            # Get recent metrics
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            metrics = (
                db.query(ProtocolMetric)
                .filter(
                    ProtocolMetric.protocol_id == protocol_id,
                    ProtocolMetric.timestamp >= cutoff_date
                )
                .order_by(ProtocolMetric.timestamp.desc())
                .limit(30)
                .all()
            )
            
            if not metrics or len(metrics) < 5:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient data for anomaly detection (minimum 5 data points required)"
                )
            
            # Engineer features (same as training)
            latest = metrics[0]
            metrics_df = pd.DataFrame([{
                'tvl': float(m.tvl) if m.tvl else 0,
                'volume_24h': float(m.volume_24h) if m.volume_24h else 0,
                'price': float(m.price) if m.price else 0,
                'price_change_24h': float(m.price_change_24h) if m.price_change_24h else 0,
            } for m in metrics])
            
            features = {
                'tvl_vol_30': metrics_df['tvl'].std() / (metrics_df['tvl'].mean() + 1e-10),
                'price_vol_30': metrics_df['price'].std() / (metrics_df['price'].mean() + 1e-10),
                'volume_vol_30': metrics_df['volume_24h'].std() / (metrics_df['volume_24h'].mean() + 1e-10),
                'tvl_slope': np.polyfit(range(len(metrics_df)), metrics_df['tvl'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'price_slope': np.polyfit(range(len(metrics_df)), metrics_df['price'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'volume_slope': np.polyfit(range(len(metrics_df)), metrics_df['volume_24h'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'liquidity_ratio': metrics_df.iloc[0]['volume_24h'] / (metrics_df.iloc[0]['tvl'] + 1e-10),
                'market_cap_to_tvl': 1.0,  # Placeholder
                'max_drawdown': float(np.min((metrics_df['price'].values - np.maximum.accumulate(metrics_df['price'].values)) / (np.maximum.accumulate(metrics_df['price'].values) + 1e-10))),
                'tvl_max_drawdown': float(np.min((metrics_df['tvl'].values - np.maximum.accumulate(metrics_df['tvl'].values)) / (np.maximum.accumulate(metrics_df['tvl'].values) + 1e-10))),
                'price_change_abs_mean': metrics_df['price_change_24h'].abs().mean(),
                'price_change_std': metrics_df['price_change_24h'].std(),
                'recent_price_change': metrics_df.iloc[0]['price_change_24h'],
                'recent_tvl': np.log1p(metrics_df.iloc[0]['tvl']),
                'recent_volume': np.log1p(metrics_df.iloc[0]['volume_24h']),
            }
            
            # Predict anomaly
            features_df = pd.DataFrame([features])
            result = detector.predict(features_df)
            
            return {
                "protocol_id": protocol_id,
                "protocol_name": protocol.name,
                "is_anomaly": result.is_anomaly,
                "anomaly_score": result.anomaly_score,
                "confidence": result.confidence,
                "algorithm_used": result.algorithm_used,
                "timestamp": datetime.utcnow().isoformat(),
                "features_analyzed": list(features.keys()),
                "alert_level": "high" if result.is_anomaly and result.anomaly_score > 0.7 else "medium" if result.is_anomaly else "low"
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(exc)}"
        )


@anomaly_router.get("/scan")
def scan_all_protocols() -> Dict[str, Any]:
    """
    Scan all active protocols for anomalies.
    
    Returns a summary of protocols with anomalous behavior detected.
    """
    from pathlib import Path
    
    detector_path = Path("models/anomaly_detector.joblib")
    
    if not detector_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Anomaly detector not trained. Please train models first."
        )
    
    try:
        from app.database.connection import SessionLocal
        from app.database.models import Protocol
        from datetime import datetime as dt
        
        db = SessionLocal()
        try:
            protocols = db.query(Protocol).filter_by(is_active=True).all()
            
            anomalies = []
            normal = []
            errors = []
            
            for protocol in protocols:
                try:
                    result = detect_protocol_anomaly(protocol.id)
                    if result["is_anomaly"]:
                        anomalies.append(result)
                    else:
                        normal.append({"protocol_id": protocol.id, "protocol_name": protocol.name})
                except HTTPException as e:
                    if e.status_code == 400:  # Insufficient data
                        errors.append({"protocol_id": protocol.id, "error": "insufficient_data"})
                    else:
                        errors.append({"protocol_id": protocol.id, "error": str(e.detail)})
            
            return {
                "total_protocols": len(protocols),
                "anomalies_detected": len(anomalies),
                "normal_protocols": len(normal),
                "errors": len(errors),
                "anomalous_protocols": anomalies,
                "timestamp": dt.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly scan failed: {str(exc)}"
        )


# Feature Importance Endpoints
feature_router = APIRouter(prefix="/features", tags=["feature-importance"])


@feature_router.get("/importance")
def get_feature_importance() -> Dict[str, Any]:
    """
    Get feature importance from trained ML risk scoring models.
    
    Returns which protocol metrics are most predictive of risk levels.
    """
    import os
    from pathlib import Path
    
    model_path = Path("models/ml_risk_scorer.joblib")
    
    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail="ML risk scorer not trained. Please train models first."
        )
    
    try:
        from app.services.ml_risk_scorer import MLRiskScorer
        
        # Load trained model
        scorer = MLRiskScorer()
        scorer.load(str(model_path))
        
        # Get feature importance from best model
        best_perf = scorer.get_best_model_performance()
        
        if not best_perf.feature_importance:
            raise HTTPException(
                status_code=404,
                detail="Feature importance not available for the best model"
            )
        
        # Sort features by importance
        sorted_features = sorted(
            best_perf.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "model_name": scorer.best_model_name,
            "model_version": "1.0",
            "total_features": len(sorted_features),
            "feature_importance": [
                {
                    "feature_name": feat,
                    "importance_score": float(importance),
                    "rank": rank
                }
                for rank, (feat, importance) in enumerate(sorted_features, 1)
            ],
            "top_5_features": [
                {"feature": feat, "importance": float(imp)}
                for feat, imp in sorted_features[:5]
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get feature importance: {str(exc)}"
        )


@feature_router.get("/shap/{protocol_id}")
def get_shap_values(protocol_id: str) -> Dict[str, Any]:
    """
    Get SHAP (SHapley Additive exPlanations) values for a specific protocol's risk prediction.
    
    SHAP values explain which features contributed most to the risk score.
    """
    import os
    from pathlib import Path
    
    model_path = Path("models/ml_risk_scorer.joblib")
    
    if not model_path.exists():
        raise HTTPException(
            status_code=503,
            detail="ML risk scorer not trained. Please train models first."
        )
    
    try:
        from app.services.ml_risk_scorer import MLRiskScorer
        from app.database.connection import SessionLocal
        from app.database.models import Protocol, ProtocolMetric
        from datetime import datetime, timedelta
        import pandas as pd
        import numpy as np
        
        # Load trained model
        scorer = MLRiskScorer()
        scorer.load(str(model_path))
        
        # Get protocol data
        db = SessionLocal()
        try:
            protocol = db.query(Protocol).filter_by(id=protocol_id).first()
            if not protocol:
                raise HTTPException(
                    status_code=404,
                    detail=f"Protocol not found: {protocol_id}"
                )
            
            # Get recent metrics and calculate SHAP values
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            metrics = (
                db.query(ProtocolMetric)
                .filter(
                    ProtocolMetric.protocol_id == protocol_id,
                    ProtocolMetric.timestamp >= cutoff_date
                )
                .order_by(ProtocolMetric.timestamp.desc())
                .limit(30)
                .all()
            )
            
            if not metrics or len(metrics) < 5:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient data for SHAP analysis (minimum 5 data points required)"
                )
            
            # Engineer features (same as training)
            metrics_df = pd.DataFrame([{
                'tvl': float(m.tvl) if m.tvl else 0,
                'volume_24h': float(m.volume_24h) if m.volume_24h else 0,
                'price': float(m.price) if m.price else 0,
                'market_cap': float(m.market_cap) if m.market_cap else 0,
                'price_change_24h': float(m.price_change_24h) if m.price_change_24h else 0,
            } for m in metrics])
            
            features = {
                'tvl_vol_30': metrics_df['tvl'].std() / (metrics_df['tvl'].mean() + 1e-10),
                'price_vol_30': metrics_df['price'].std() / (metrics_df['price'].mean() + 1e-10),
                'volume_vol_30': metrics_df['volume_24h'].std() / (metrics_df['volume_24h'].mean() + 1e-10),
                'tvl_slope': np.polyfit(range(len(metrics_df)), metrics_df['tvl'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'price_slope': np.polyfit(range(len(metrics_df)), metrics_df['price'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'volume_slope': np.polyfit(range(len(metrics_df)), metrics_df['volume_24h'].values, 1)[0] if len(metrics_df) > 1 else 0,
                'liquidity_ratio': metrics_df.iloc[0]['volume_24h'] / (metrics_df.iloc[0]['tvl'] + 1e-10),
                'market_cap_to_tvl': metrics_df.iloc[0]['market_cap'] / (metrics_df.iloc[0]['tvl'] + 1e-10),
                'max_drawdown': float(np.min((metrics_df['price'].values - np.maximum.accumulate(metrics_df['price'].values)) / (np.maximum.accumulate(metrics_df['price'].values) + 1e-10))),
                'tvl_max_drawdown': float(np.min((metrics_df['tvl'].values - np.maximum.accumulate(metrics_df['tvl'].values)) / (np.maximum.accumulate(metrics_df['tvl'].values) + 1e-10))),
                'price_change_abs_mean': metrics_df['price_change_24h'].abs().mean(),
                'price_change_std': metrics_df['price_change_24h'].std(),
                'protocol_category': 0,  # Placeholder
                'protocol_chain': 0,  # Placeholder
                'recent_price_change': metrics_df.iloc[0]['price_change_24h'],
                'recent_tvl': np.log1p(metrics_df.iloc[0]['tvl']),
                'recent_volume': np.log1p(metrics_df.iloc[0]['volume_24h']),
            }
            
            # Get SHAP values
            features_df = pd.DataFrame([features])
            shap_values = scorer.explain_prediction(features_df)
            
            if not shap_values:
                return {
                    "protocol_id": protocol_id,
                    "protocol_name": protocol.name,
                    "message": "SHAP values not available (model may not support SHAP)",
                    "feature_contributions": []
                }
            
            # Sort by absolute SHAP value
            sorted_shap = sorted(
                shap_values.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            return {
                "protocol_id": protocol_id,
                "protocol_name": protocol.name,
                "model_used": scorer.best_model_name,
                "shap_values": [
                    {
                        "feature": feat,
                        "shap_value": float(val),
                        "impact": "increases_risk" if val > 0 else "decreases_risk",
                        "magnitude": abs(float(val))
                    }
                    for feat, val in sorted_shap
                ],
                "top_5_contributors": [
                    {"feature": feat, "shap_value": float(val)}
                    for feat, val in sorted_shap[:5]
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"SHAP analysis failed: {str(exc)}"
        )


