"""
Seed database with real DeFi protocols for production use.

This script adds major, real DeFi protocols across different categories
with verified contract addresses and chains.
"""
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.exc import IntegrityError

from app.database.connection import managed_session
from app.database.models import Protocol, ProtocolCategoryEnum


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("scripts.seed_real_protocols")


# Real DeFi Protocols with verified data
REAL_PROTOCOLS = [
    # DEX Protocols
    {
        "name": "Uniswap",
        "symbol": "UNI",
        "contract_address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "ethereum",
    },
    {
        "name": "PancakeSwap",
        "symbol": "CAKE",
        "contract_address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "bsc",
    },
    {
        "name": "SushiSwap",
        "symbol": "SUSHI",
        "contract_address": "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "ethereum",
    },
    {
        "name": "Curve",
        "symbol": "CRV",
        "contract_address": "0xD533a949740bb3306d119CC777fa900bA034cd52",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "ethereum",
    },
    # Lending Protocols
    {
        "name": "Aave",
        "symbol": "AAVE",
        "contract_address": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
        "category": ProtocolCategoryEnum.LENDING,
        "chain": "ethereum",
    },
    {
        "name": "Compound",
        "symbol": "COMP",
        "contract_address": "0xc00e94Cb662C3520282E6f5717214004A7f26888",
        "category": ProtocolCategoryEnum.LENDING,
        "chain": "ethereum",
    },
    {
        "name": "MakerDAO",
        "symbol": "MKR",
        "contract_address": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
        "category": ProtocolCategoryEnum.LENDING,
        "chain": "ethereum",
    },
    # Yield Aggregators
    {
        "name": "Yearn Finance",
        "symbol": "YFI",
        "contract_address": "0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e",
        "category": ProtocolCategoryEnum.YIELD,
        "chain": "ethereum",
    },
    {
        "name": "Convex Finance",
        "symbol": "CVX",
        "contract_address": "0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
        "category": ProtocolCategoryEnum.YIELD,
        "chain": "ethereum",
    },
    # Liquid Staking
    {
        "name": "Lido",
        "symbol": "LDO",
        "contract_address": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
        "category": ProtocolCategoryEnum.STAKING,
        "chain": "ethereum",
    },
    {
        "name": "Rocket Pool",
        "symbol": "RPL",
        "contract_address": "0xD33526068D116cE69F19A9ee46F0bd304F21A51f",
        "category": ProtocolCategoryEnum.STAKING,
        "chain": "ethereum",
    },
    # Derivatives
    {
        "name": "dYdX",
        "symbol": "DYDX",
        "contract_address": "0x92D6C1e31e14520e676a687F0a93788B716BEff5",
        "category": ProtocolCategoryEnum.DERIVATIVES,
        "chain": "ethereum",
    },
    {
        "name": "GMX",
        "symbol": "GMX",
        "contract_address": "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a",
        "category": ProtocolCategoryEnum.DERIVATIVES,
        "chain": "arbitrum",
    },
    # Bridges
    {
        "name": "Stargate Finance",
        "symbol": "STG",
        "contract_address": "0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6",
        "category": ProtocolCategoryEnum.BRIDGE,
        "chain": "ethereum",
    },
    # Layer 2 / Additional Popular Protocols
    {
        "name": "Balancer",
        "symbol": "BAL",
        "contract_address": "0xba100000625a3754423978a60c9317c58a424e3D",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "ethereum",
    },
    {
        "name": "1inch",
        "symbol": "1INCH",
        "contract_address": "0x111111111117dC0aa78b770fA6A738034120C302",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "ethereum",
    },
    {
        "name": "Frax Finance",
        "symbol": "FXS",
        "contract_address": "0x3432B6A60D23Ca0dFCa7761B7ab56459D9C964D0",
        "category": ProtocolCategoryEnum.LENDING,
        "chain": "ethereum",
    },
    {
        "name": "Synapse",
        "symbol": "SYN",
        "contract_address": "0x0f2D719407FdBeFF09D87557AbB7232601FD9F29",
        "category": ProtocolCategoryEnum.BRIDGE,
        "chain": "ethereum",
    },
    {
        "name": "Osmosis",
        "symbol": "OSMO",
        "contract_address": None,  # Cosmos chain
        "category": ProtocolCategoryEnum.DEX,
        "chain": "cosmos",
    },
    {
        "name": "Trader Joe",
        "symbol": "JOE",
        "contract_address": "0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd",
        "category": ProtocolCategoryEnum.DEX,
        "chain": "avalanche",
    },
]


def main() -> None:
    """Add real DeFi protocols to the database."""
    logger.info(f"🚀 Seeding {len(REAL_PROTOCOLS)} real DeFi protocols...")
    
    added_count = 0
    skipped_count = 0
    
    try:
        with managed_session() as db:
            for proto_data in REAL_PROTOCOLS:
                try:
                    # Check if protocol already exists
                    existing = db.query(Protocol).filter_by(name=proto_data["name"]).first()
                    if existing:
                        logger.info(f"⏭️  Skipped: {proto_data['name']} (already exists)")
                        skipped_count += 1
                        continue
                    
                    protocol = Protocol(
                        name=proto_data["name"],
                        symbol=proto_data["symbol"],
                        contract_address=proto_data["contract_address"],
                        category=proto_data["category"],
                        chain=proto_data["chain"],
                        is_active=True,
                    )
                    db.add(protocol)
                    db.flush()  # Get ID immediately
                    
                    logger.info(f"✅ Added: {proto_data['name']} ({proto_data['symbol']}) on {proto_data['chain']}")
                    added_count += 1
                    
                except IntegrityError as e:
                    db.rollback()
                    logger.warning(f"⚠️  Duplicate: {proto_data['name']} - {e}")
                    skipped_count += 1
                    continue
            
            db.commit()
        
        logger.info("=" * 60)
        logger.info(f"✅ Successfully added: {added_count} protocols")
        logger.info(f"⏭️  Skipped (already exist): {skipped_count} protocols")
        logger.info(f"📊 Total in system: {added_count + skipped_count} protocols")
        logger.info("=" * 60)
        logger.info("🎉 Real protocol seeding completed!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Run data collection: python scripts/collect_live_data.py")
        logger.info("2. Calculate risk scores: python scripts/calculate_risks.py")
        logger.info("3. Start the backend server: uvicorn app.main:app --reload")
        
    except Exception as exc:
        logger.exception(f"❌ Seeding failed: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()




