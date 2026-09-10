"""FastAPI application factory."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.database.session import get_db


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="0.1.0",
        description=(
            "REST API for the Student Clearance Management System. "
            "Students submit one clearance request; each required department "
            "reviews its own task; the overall status is derived from those tasks."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Exact origins only. Never "*" together with allow_credentials.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.get("/health", tags=["system"], summary="Liveness and database check")
    def health(db: Session = Depends(get_db)) -> dict:
        """Prove the API is up *and* that it can reach PostgreSQL.

        A health check that does not touch the database will happily report
        success while every real endpoint fails, so this one runs a query.
        """
        try:
            db.execute(text("SELECT 1"))
            database = "connected"
        except Exception as exc:  # noqa: BLE001 - report, don't crash the check
            database = f"unavailable: {type(exc).__name__}"

        return {
            "status": "ok",
            "environment": settings.ENVIRONMENT,
            "database": database,
        }

    # Routers are registered here as each phase lands:
    # app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
