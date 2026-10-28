"""Standard response envelope used by all data endpoints.

Success: {"status": "success", "data": {...}}
Error:   {"status": "error", "message": "...", "errors": [...]}
"""

from typing import Any, Literal

from pydantic import BaseModel


class SuccessEnvelope[DataT](BaseModel):
    status: Literal["success"] = "success"
    data: DataT


class ErrorEnvelope(BaseModel):
    status: Literal["error"] = "error"
    message: str
    # Field-level details attached by validation errors, if any.
    errors: list[dict[str, Any]] | None = None
