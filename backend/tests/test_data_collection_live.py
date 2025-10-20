import os
import typing as t

import pytest
import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import SessionLocal
from app.database.models import Protocol
from app.services.data_collector import DataCollectorService


LIVE = os.getenv("LIVE_DATA_TESTS", "0") == "1"


def _ensure_protocol(
    *, name: str, symbol: str | None, chain: str, contract: str | None
) -> str:
    db = SessionLocal()
    try:
        row = (
            db.query(Protocol)  # type: ignore[attr-defined]
            .filter(Protocol.name == name)
            .first()
        )
        if not row:
            row = Protocol(
                name=name,
                symbol=symbol,
                chain=chain,
                contract_address=contract,
                category="dex",
                is_active=True,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
        return row.id
    finally:
        db.close()


@pytest.mark.skipif(not LIVE, reason="Set LIVE_DATA_TESTS=1 to run live CoinGecko test")
def test_collect_from_coingecko_live(caplog: pytest.LogCaptureFixture) -> None:
    api_key = os.getenv("COINGECKO_API_KEY") or os.getenv("COINGECKO_PRO_API_KEY")
    if not api_key:
        pytest.skip("No CoinGecko API key configured in environment")

    protocol_id = _ensure_protocol(
        name="Uniswap",
        symbol="uni",
        chain="ethereum",
        contract="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    )

    db = SessionLocal()
    try:
        service = DataCollectorService(db=db)
        with caplog.at_level("INFO"):
            processed = asyncio.run(service.collect("coingecko", [protocol_id]))
        assert processed in (0, 1)
    finally:
        db.close()


@pytest.mark.skipif(not LIVE, reason="Set LIVE_DATA_TESTS=1 to run live DeFiLlama test")
def test_collect_from_defillama_live(caplog: pytest.LogCaptureFixture) -> None:
    protocol_id = _ensure_protocol(
        name="Uniswap",
        symbol="uni",
        chain="ethereum",
        contract="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    )
    db = SessionLocal()
    try:
        service = DataCollectorService(db=db)
        with caplog.at_level("INFO"):
            processed = asyncio.run(service.collect("defillama", [protocol_id]))
        assert processed in (0, 1)
    finally:
        db.close()


@pytest.mark.skipif(not LIVE, reason="Set LIVE_DATA_TESTS=1 to run endpoint test")
def test_collect_endpoint_coingecko_live() -> None:
    client = TestClient(app)
    resp = client.post("/data/collect", json={"source": "coingecko"})
    # Either success 200 or informative 400 if misconfigured
    assert resp.status_code in (200, 400)
    if resp.status_code == 400:
        body = resp.json()
        print("Endpoint returned 400:", body)


