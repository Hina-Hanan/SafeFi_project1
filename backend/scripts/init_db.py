import logging
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import ENGINE
from app.database.models import Base


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s [%(name)s] %(message)s")
logger = logging.getLogger("scripts.init_db")


def main() -> None:
    logger.info("Starting database initialization")
    try:
        Base.metadata.create_all(bind=ENGINE)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as exc:
        logger.exception("Failed to create tables: %s", exc)
        raise SystemExit(1)


if __name__ == "__main__":
    main()



