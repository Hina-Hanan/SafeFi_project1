import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolMetric, RiskScore, User, Alert, RiskLevelEnum, ProtocolCategoryEnum


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("scripts.seed_data")


def main() -> None:
    logger.info("Seeding sample data")
    try:
        with managed_session() as db:
            protocol = Protocol(
                name="Uniswap",
                symbol="UNI",
                contract_address="0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
                category=ProtocolCategoryEnum.DEX,
                chain="ethereum",
                is_active=True,
            )
            db.add(protocol)
            db.flush()

            now = datetime.now(timezone.utc)
            metrics = [
                ProtocolMetric(
                    protocol_id=protocol.id,
                    tvl=1000000000.0,
                    volume_24h=50000000.0,
                    price=6.25,
                    market_cap=3500000000.0,
                    price_change_24h=1.5,
                    timestamp=now - timedelta(hours=4 * i),
                )
                for i in range(5)
            ]
            db.add_all(metrics)

            risk = RiskScore(
                protocol_id=protocol.id,
                risk_level=RiskLevelEnum.MEDIUM,
                risk_score=0.45,
                volatility_score=0.3,
                liquidity_score=0.7,
                model_version="v1.0.0",
                timestamp=now,
            )
            db.add(risk)

            user = User(
                email="test@example.com",
                encrypted_password="hashedpassword",
                subscription_tier="free",
            )
            db.add(user)
            db.flush()

            alert = Alert(
                user_id=user.id,
                protocol_id=protocol.id,
                risk_threshold=0.6,
                is_active=True,
            )
            db.add(alert)

        logger.info("Seeding completed")
    except SQLAlchemyError as exc:
        logger.exception("Seeding failed: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()



