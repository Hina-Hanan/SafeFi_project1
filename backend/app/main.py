import logging
import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.connection import get_db
from app.api.router import api_router
from app.startup import lifespan


def _configure_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


_configure_logging()
logger = logging.getLogger("app.main")


def create_app() -> FastAPI:
    app = FastAPI(
        title="DeFi Risk Assessment API",
        version="1.0.0",
        lifespan=lifespan
    )

    # CORS
    allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in allowed_origins if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_, exc: Exception) -> JSONResponse:  # type: ignore[override]
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(status_code=500, content={"data": None, "meta": {"error": "Internal Server Error"}})

    @app.get("/", tags=["root"])  # Convenience root
    async def root() -> dict[str, Any]:
        return {
            "data": {"message": "DeFi Risk Assessment API"},
            "meta": {"docs": "/docs", "health": "/health"},
        }

    # Mount API router FIRST (provides dependency injection of DB via dependencies parameter when needed in subroutes)
    # This includes the proper /health endpoint from health.py
    app.include_router(api_router, prefix="")

    return app


app = create_app()
