import uvicorn
from fastapi import FastAPI

from api.core.config import settings
from api.core.errors import register_error_handlers
from api.routers import auth, health


def create_app() -> FastAPI:
    """Application factory for the FindArtisan API."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    register_error_handlers(app)

    app.include_router(health.router)
    app.include_router(auth.router)

    return app


app = create_app()


def main() -> None:
    """Run the development server."""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
