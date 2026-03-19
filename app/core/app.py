# app/core/app.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import api_router

def create_app() -> FastAPI:
    """
    Application factory for creating the FastAPI app.
    Keeps initialization clean and structured.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register versioned API routes
    app.include_router(api_router, prefix="/api/ats")

    @app.get("/")
    def homepage():
        return {"message": "successfully landed"}

    return app