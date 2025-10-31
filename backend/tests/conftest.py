"""
Test configuration and fixtures for DeFi Risk Assessment project.

Provides common test utilities, database fixtures, and mock services
for comprehensive unit testing of all service layers.
"""

import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator, Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["TESTING"] = "true"
# DATABASE_URL should be set from environment or .env file (PostgreSQL)
# Default to test database if not set
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "postgresql+psycopg2://defi_user:usersafety@localhost:5432/defi_risk_assessment"
# Disable MLflow for tests - use file-based tracking to avoid connection errors
os.environ["MLFLOW_TRACKING_URI"] = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
os.environ["LOG_LEVEL"] = "WARNING"

from app.main import app
from app.database.connection import get_db, SessionLocal
from app.database.models import Base, Protocol, ProtocolMetric, RiskScore, User, Alert
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create database tables once per test session. Auto-use for all tests."""
    from app.database.connection import ENGINE
    
    # Create all tables
    try:
        Base.metadata.create_all(bind=ENGINE)
        logger.info("✅ Database tables created for tests")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise
    
    yield
    
    # Optionally drop tables after all tests (comment out to keep data)
    # Base.metadata.drop_all(bind=ENGINE)


@pytest.fixture(scope="function")
def test_db(setup_database) -> Generator[Session, None, None]:
    """
    Create a test database session with PostgreSQL.
    
    Uses the DATABASE_URL from environment, which should point to PostgreSQL.
    Tables are created once per session via setup_database fixture.
    
    Returns:
        Database session for testing
    """
    from app.database.connection import SessionLocal
    
    # Create session using the app's SessionLocal
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture(scope="function")
def test_client(setup_database, test_db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with database dependency override.
    
    Args:
        setup_database: Ensures tables are created before test (session-scoped)
        test_db: Test database session
        
    Returns:
        FastAPI test client
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_protocol_data() -> Dict[str, Any]:
    """Sample protocol data for testing."""
    return {
        "id": "test-protocol-1",
        "name": "Test Protocol",
        "symbol": "TEST",
        "contract_address": "0x1234567890123456789012345678901234567890",
        "category": "lending",
        "chain": "ethereum",
        "is_active": True
    }


@pytest.fixture
def sample_protocol(test_db: Session, sample_protocol_data: Dict[str, Any]) -> Protocol:
    """Create a sample protocol in the test database."""
    protocol = Protocol(**sample_protocol_data)
    test_db.add(protocol)
    test_db.commit()
    test_db.refresh(protocol)
    return protocol


@pytest.fixture
def sample_metrics_data() -> List[Dict[str, Any]]:
    """Sample protocol metrics data for testing."""
    base_time = datetime.utcnow()
    return [
        {
            "protocol_id": "test-protocol-1",
            "tvl": 1000000.0,
            "volume_24h": 50000.0,
            "price": 100.0,
            "market_cap": 10000000.0,
            "price_change_24h": 0.05,
            "timestamp": base_time - timedelta(days=30)
        },
        {
            "protocol_id": "test-protocol-1",
            "tvl": 1100000.0,
            "volume_24h": 55000.0,
            "price": 105.0,
            "market_cap": 10500000.0,
            "price_change_24h": 0.03,
            "timestamp": base_time - timedelta(days=15)
        },
        {
            "protocol_id": "test-protocol-1",
            "tvl": 1200000.0,
            "volume_24h": 60000.0,
            "price": 110.0,
            "market_cap": 11000000.0,
            "price_change_24h": 0.02,
            "timestamp": base_time
        }
    ]


@pytest.fixture
def sample_metrics(test_db: Session, sample_metrics_data: List[Dict[str, Any]]) -> List[ProtocolMetric]:
    """Create sample protocol metrics in the test database."""
    metrics = []
    for metric_data in sample_metrics_data:
        metric = ProtocolMetric(**metric_data)
        test_db.add(metric)
        metrics.append(metric)
    
    test_db.commit()
    for metric in metrics:
        test_db.refresh(metric)
    return metrics


@pytest.fixture
def sample_risk_score_data() -> Dict[str, Any]:
    """Sample risk score data for testing."""
    return {
        "protocol_id": "test-protocol-1",
        "risk_level": "medium",
        "risk_score": 0.65,
        "volatility_score": 0.7,
        "liquidity_score": 0.6,
        "model_version": "v1.0",
        "timestamp": datetime.utcnow()
    }


@pytest.fixture
def sample_risk_score(test_db: Session, sample_risk_score_data: Dict[str, Any]) -> RiskScore:
    """Create a sample risk score in the test database."""
    risk_score = RiskScore(**sample_risk_score_data)
    test_db.add(risk_score)
    test_db.commit()
    test_db.refresh(risk_score)
    return risk_score


@pytest.fixture
def mock_coingecko_response() -> Dict[str, Any]:
    """Mock CoinGecko API response."""
    return {
        "id": "test-protocol",
        "symbol": "test",
        "name": "Test Protocol",
        "current_price": 100.0,
        "market_cap": 10000000,
        "total_volume": 50000,
        "price_change_percentage_24h": 5.0,
        "market_cap_change_percentage_24h": 3.0
    }


@pytest.fixture
def mock_defillama_response() -> Dict[str, Any]:
    """Mock DeFiLlama API response."""
    return {
        "name": "Test Protocol",
        "symbol": "TEST",
        "tvl": 1000000,
        "chain": "Ethereum",
        "category": "lending",
        "change_1d": 0.05,
        "change_7d": 0.15,
        "change_30d": 0.25
    }


@pytest.fixture
def mock_mlflow_run() -> Mock:
    """Mock MLflow run for testing."""
    mock_run = Mock()
    mock_run.info.run_id = "test-run-id"
    mock_run.info.experiment_id = "test-experiment-id"
    mock_run.data.metrics = {
        "accuracy": 0.85,
        "f1_score": 0.82,
        "precision": 0.80,
        "recall": 0.85
    }
    mock_run.data.params = {
        "n_estimators": "100",
        "max_depth": "10"
    }
    return mock_run


@pytest.fixture
def mock_vector_store() -> Mock:
    """Mock vector store for RAG testing."""
    mock_store = Mock()
    mock_store.similarity_search.return_value = [
        Mock(page_content="Test protocol has high TVL and low risk"),
        Mock(page_content="Protocol metrics show stable performance")
    ]
    mock_store.add_documents.return_value = ["doc1", "doc2"]
    return mock_store


@pytest.fixture
def mock_llm_response() -> str:
    """Mock LLM response for RAG testing."""
    return "Based on the context, Test Protocol shows medium risk with stable TVL growth."


@pytest.fixture
def sample_feature_data() -> pd.DataFrame:
    """Sample feature data for ML testing."""
    np.random.seed(42)
    return pd.DataFrame({
        "tvl_vol_30": np.random.normal(0.1, 0.05, 100),
        "price_vol_30": np.random.normal(0.15, 0.08, 100),
        "volume_vol_30": np.random.normal(0.2, 0.1, 100),
        "mc_vol_30": np.random.normal(0.12, 0.06, 100),
        "price_slope": np.random.normal(0.02, 0.01, 100),
        "tvl_slope": np.random.normal(0.03, 0.02, 100),
        "liquidity_ratio_30": np.random.normal(0.5, 0.2, 100),
        "tvl_trend_7": np.random.normal(0.01, 0.005, 100),
        "price_momentum": np.random.normal(0.02, 0.01, 100),
        "volume_consistency": np.random.normal(0.8, 0.1, 100),
        "market_cap_stability": np.random.normal(0.7, 0.15, 100),
        "drawdown_risk": np.random.normal(0.1, 0.05, 100)
    })


@pytest.fixture
def sample_risk_labels() -> List[str]:
    """Sample risk labels for ML testing."""
    return ["low"] * 40 + ["medium"] * 35 + ["high"] * 25


@pytest.fixture
def mock_email_service() -> Mock:
    """Mock email service for testing."""
    mock_service = Mock()
    mock_service.send_alert.return_value = True
    mock_service.send_bulk_alerts.return_value = {"sent": 5, "failed": 0}
    return mock_service


@pytest.fixture
def mock_rate_limiter() -> Mock:
    """Mock rate limiter for testing."""
    mock_limiter = Mock()
    mock_limiter.acquire.return_value = True
    mock_limiter.is_limited.return_value = False
    return mock_limiter


@pytest.fixture
def mock_anomaly_data() -> pd.DataFrame:
    """Sample data for anomaly detection testing."""
    np.random.seed(42)
    normal_data = np.random.normal(0, 1, (90, 5))
    anomaly_data = np.random.normal(5, 0.5, (10, 5))
    all_data = np.vstack([normal_data, anomaly_data])
    
    return pd.DataFrame(all_data, columns=[f"feature_{i}" for i in range(5)])


@pytest.fixture
def mock_document_loader() -> Mock:
    """Mock document loader for RAG testing."""
    mock_loader = Mock()
    mock_loader.load_protocols.return_value = [
        Mock(page_content="Protocol A: High TVL, Low Risk"),
        Mock(page_content="Protocol B: Medium TVL, Medium Risk")
    ]
    mock_loader.load_metrics.return_value = [
        Mock(page_content="TVL: 1M, Volume: 50K"),
        Mock(page_content="Price: $100, Change: +5%")
    ]
    mock_loader.load_risk_scores.return_value = [
        Mock(page_content="Risk Score: 0.3 (Low)"),
        Mock(page_content="Risk Score: 0.7 (High)")
    ]
    return mock_loader


# Async fixtures for testing async services
@pytest.fixture
async def async_test_client(test_db: Session) -> AsyncGenerator[TestClient, None]:
    """Async test client for testing async endpoints."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


# Utility functions for tests
def assert_valid_uuid(uuid_string: str) -> None:
    """Assert that a string is a valid UUID."""
    import uuid
    try:
        uuid.UUID(uuid_string)
    except ValueError:
        pytest.fail(f"Invalid UUID: {uuid_string}")


def assert_valid_timestamp(timestamp: datetime) -> None:
    """Assert that a timestamp is valid."""
    assert isinstance(timestamp, datetime)
    assert timestamp.tzinfo is not None  # Should be timezone-aware


def assert_valid_risk_score(score: float) -> None:
    """Assert that a risk score is valid."""
    assert isinstance(score, (int, float))
    assert 0.0 <= score <= 1.0


def assert_valid_risk_level(level: str) -> None:
    """Assert that a risk level is valid."""
    assert level in ["low", "medium", "high"]


def create_test_protocol(
    db: Session,
    name: str = "Test Protocol",
    category: str = "lending",
    **kwargs
) -> Protocol:
    """Helper function to create a test protocol."""
    protocol_data = {
        "name": name,
        "symbol": name.upper()[:4],
        "category": category,
        "chain": "ethereum",
        "is_active": True,
        **kwargs
    }
    protocol = Protocol(**protocol_data)
    db.add(protocol)
    db.commit()
    db.refresh(protocol)
    return protocol


def create_test_metrics(
    db: Session,
    protocol_id: str,
    count: int = 5,
    **kwargs
) -> List[ProtocolMetric]:
    """Helper function to create test metrics."""
    metrics = []
    base_time = datetime.utcnow()
    
    for i in range(count):
        metric_data = {
            "protocol_id": protocol_id,
            "tvl": 1000000.0 + (i * 100000),
            "volume_24h": 50000.0 + (i * 5000),
            "price": 100.0 + (i * 5),
            "market_cap": 10000000.0 + (i * 1000000),
            "price_change_24h": 0.05 + (i * 0.01),
            "timestamp": base_time - timedelta(days=i),
            **kwargs
        }
        metric = ProtocolMetric(**metric_data)
        db.add(metric)
        metrics.append(metric)
    
    db.commit()
    for metric in metrics:
        db.refresh(metric)
    return metrics


def create_test_risk_score(
    db: Session,
    protocol_id: str,
    risk_level: str = "medium",
    risk_score: float = 0.5,
    **kwargs
) -> RiskScore:
    """Helper function to create a test risk score."""
    risk_data = {
        "protocol_id": protocol_id,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "volatility_score": 0.6,
        "liquidity_score": 0.4,
        "model_version": "v1.0",
        "timestamp": datetime.utcnow(),
        **kwargs
    }
    risk_score_obj = RiskScore(**risk_data)
    db.add(risk_score_obj)
    db.commit()
    db.refresh(risk_score_obj)
    return risk_score_obj

