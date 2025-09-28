"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import api_router
from settings import Settings, get_settings


def create_app() -> FastAPI:
    """Application factory for the API."""

    app = FastAPI(title="Gastos Delivery API", version="0.1.0")

    settings = get_settings()
    origins = settings.resolved_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["meta"])
    def health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
        return {"status": "ok", "tz": settings.tz}

    return app


app = create_app()
