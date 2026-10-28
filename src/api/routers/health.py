from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from api.core.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    healthy: bool
    service: str
    version: str
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the current health status of the API.",
)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        healthy=True,
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(tz=UTC),
    )
