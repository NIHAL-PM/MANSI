from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _secret() -> bytes:
    secret = get_settings().auth_jwt_secret
    if not secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
    return secret.encode()


def mint_token(subject: UUID, token_type: str, extra: dict[str, str] | None = None) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(seconds=get_settings().stream_token_ttl_seconds)
    payload = {"sub": str(subject), "typ": token_type, "exp": int(expires_at.timestamp()), **(extra or {})}
    encoded = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode()) + "." + _b64(json.dumps(payload, separators=(",", ":")).encode())
    signature = _b64(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
    return f"{encoded}.{signature}", expires_at


def decode_token(token: str, expected_type: str) -> dict[str, str | int]:
    try:
        encoded, signature = token.rsplit(".", 1)
        expected = _b64(hmac.new(_secret(), encoded.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        payload = json.loads(_unb64(encoded.split(".")[1]))
        if payload["typ"] != expected_type or int(payload["exp"]) <= int(datetime.now(UTC).timestamp()):
            raise ValueError("wrong type or expired")
        UUID(str(payload["sub"]))
        return payload
    except (KeyError, ValueError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired credential") from None


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer credential required")
    return authorization[7:]


def current_user(authorization: str | None = Header(default=None)) -> UUID:
    return UUID(str(decode_token(_bearer(authorization), "user")["sub"]))


def current_stream(authorization: str | None = Header(default=None)) -> dict[str, str | int]:
    return decode_token(_bearer(authorization), "stream")
