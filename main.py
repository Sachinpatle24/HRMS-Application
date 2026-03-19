# app/main.py

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.core.logger import configure_logging, get_custom_logger
configure_logging(app_name="ats-backend")
logger = get_custom_logger(app_name="main")

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.app import create_app
from app.core.database import init_db
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("FastAPI application started")

    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception:
        if settings.REQUIRE_DB_AT_STARTUP:
            logger.exception("Database required but unavailable")
            raise
        else:
            logger.warning("Database unavailable — continuing without it (DB features disabled)", exc_info=True)

    yield

    logger.info("FastAPI application stopped")
    from app.core.database import engine  
    await engine.dispose()

def get_application() -> FastAPI:
    app = create_app()
    app.router.lifespan_context = lifespan
    return app

app = get_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT_NO, reload=True)
