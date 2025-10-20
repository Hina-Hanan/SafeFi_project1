from mlflow import MlflowClient
from app.core.config import settings


def get_mlflow_client() -> MlflowClient:
    return MlflowClient(tracking_uri=settings.mlflow_tracking_uri)


def predict_risk(features: dict) -> float:
    # TODO: load model from MLflow registry and predict
    # Placeholder returns mid risk
    return 0.5



