"""Global exception handlers that render errors in the standard envelope."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _error_content(message: str, errors: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    content: dict[str, Any] = {"status": "error", "message": message}
    if errors:
        content["errors"] = errors
    return content


def _validation_errors(exc: RequestValidationError) -> list[dict[str, Any]]:
    """Normalize validation errors; drop raw input (may echo secrets like passwords)."""
    return [
        {"loc": error.get("loc"), "msg": error.get("msg"), "type": error.get("type")}
        for error in exc.errors()
    ]


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, str):
            message = exc.detail
            errors = None
        else:
            message = "Request failed."
            errors = jsonable_encoder(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_content(message, errors),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_content("Validation failed.", _validation_errors(exc)),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_content("Internal server error."),
        )
