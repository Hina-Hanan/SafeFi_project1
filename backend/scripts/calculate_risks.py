"""
Calculate risk scores for all active protocols using ML models.

This script uses the RiskCalculatorService to generate risk assessments
based on collected metrics. Should be run after data collection.
"""
import logging
import sys
from datetime import datetime
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.risk_calculator import RiskCalculatorService
from app.database.connection import managed_session
from app.database.models import RiskScore


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("scripts.calculate_risks")


def main() -> None:
    """Calculate and store risk scores for all protocols."""
    logger.info("=" * 60)
    logger.info("🧮 Starting risk score calculation...")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 60)
    
    try:
        # Initialize service (will use file-based MLflow tracking if server not running)
        service = RiskCalculatorService()
        
        # Generate batch predictions
        logger.info("📊 Generating risk predictions for all active protocols...")
        results = service.predict_batch()
        
        logger.info("=" * 60)
        logger.info(f"✅ Successfully calculated risks for {len(results)} protocols")
        logger.info("=" * 60)
        
        # Show summary
        risk_levels = {"low": 0, "medium": 0, "high": 0}
        for result in results:
            risk_levels[result.get("risk_level", "medium")] += 1
        
        logger.info("📊 Risk Distribution:")
        logger.info(f"   🟢 Low Risk: {risk_levels['low']}")
        logger.info(f"   🟡 Medium Risk: {risk_levels['medium']}")
        logger.info(f"   🔴 High Risk: {risk_levels['high']}")
        logger.info("=" * 60)
        # --- MLflow logging ---
        try:
            import mlflow
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment("defi-risk")
            with mlflow.start_run(run_name=f"risk-batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"):
                mlflow.log_param("job_type", "batch_risk_calc")
                model_version = getattr(service, "model_version", "baseline")
                mlflow.log_param("model_version", str(model_version))
                mlflow.log_metric("protocols_scored", len(results))
                mlflow.log_metric("count_low", risk_levels["low"]) 
                mlflow.log_metric("count_medium", risk_levels["medium"]) 
                mlflow.log_metric("count_high", risk_levels["high"]) 
        except Exception as ml_e:
            logger.warning(f"MLflow logging skipped: {ml_e}")
        # --- end MLflow logging ---

        logger.info("🎉 Risk calculation completed!")
        logger.info("")
        logger.info("✨ Your dashboard is now ready with real-time data!")
        
    except Exception as e:
        logger.exception(f"❌ Risk calculation failed: {e}")
        logger.info("")
        logger.info("💡 Note: If MLflow connection failed, that's OK!")
        logger.info("   The system will use rule-based risk scoring instead.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()




