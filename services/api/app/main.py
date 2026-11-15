from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.api.v1 import context, devices, streams

settings = get_settings()
app = FastAPI(title="MANSI API", version="1.0.0", docs_url="/docs" if settings.environment != "production" else None)
app.include_router(devices.router, prefix=settings.api_prefix)
app.include_router(streams.router, prefix=settings.api_prefix)
app.include_router(context.router, prefix=settings.api_prefix)


@app.on_event("startup")
async def refuse_ephemeral_storage_in_production() -> None:
    if settings.environment in {"staging", "production"}:
        raise RuntimeError("SupabaseRepository is required before staging or production startup")


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id", str(uuid4()))
    request.state.trace_id = trace_id
    started = perf_counter()
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    response.headers["x-response-time-ms"] = str(round((perf_counter() - started) * 1000, 2))
    return response


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok", "service": settings.service_name}


@app.get("/ready", include_in_schema=False)
async def readiness() -> JSONResponse:
    missing = [name for name, value in {"SUPABASE_URL": settings.supabase_url, "SUPABASE_ANON_KEY": settings.supabase_anon_key, "REDIS_URL": settings.redis_url, "AUTH_JWT_SECRET": settings.auth_jwt_secret}.items() if not value]
    if missing and settings.environment in {"staging", "production"}:
        return JSONResponse(status_code=503, content={"status": "not_ready", "missing": missing})
    return JSONResponse(status_code=200, content={"status": "ready", "dependencies": "deferred"})
