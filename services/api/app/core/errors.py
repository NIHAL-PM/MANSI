from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def problem(status: int, title: str, detail: str, trace_id: str) -> JSONResponse:
    return JSONResponse(status_code=status, media_type="application/problem+json", content={
        "type": f"https://mansi.invalid/problems/{title.lower().replace(' ', '-')}",
        "title": title, "status": status, "detail": detail, "trace_id": trace_id,
    })


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return problem(422, "Validation failed", "Request did not match the API contract", getattr(request.state, "trace_id", str(uuid4())))
