import logging
import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session


load_dotenv()

logger = logging.getLogger("app.database.connection")


def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in environment or .env file")
    return url


def _create_engine() -> Engine:
    database_url = _get_database_url()
    engine = create_engine(
        database_url,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
        isolation_level=os.getenv("DB_ISOLATION_LEVEL", "READ COMMITTED"),
        future=True,
    )

    # pool_pre_ping already validates connections without starting a transaction.
    # Avoid custom pings that can trigger autobegin under SQLAlchemy 2.0.

    return engine


ENGINE: Engine = _create_engine()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a transactional session with cleanup.

    Yields:
        Session: SQLAlchemy session bound to pooled engine.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as sa_err:
        db.rollback()
        logger.exception("Database error; transaction rolled back: %s", sa_err)
        raise
    except Exception as exc:  # pragma: no cover - propagate
        db.rollback()
        logger.exception("Unhandled error in DB session: %s", exc)
        raise
    finally:
        db.close()


@contextmanager
def managed_session() -> Generator[Session, None, None]:
    """Context manager for non-FastAPI usage.

    Example:
        with managed_session() as db:
            db.execute(...)
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as sa_err:
        db.rollback()
        logger.exception("Database error; transaction rolled back: %s", sa_err)
        raise
    finally:
        db.close()


