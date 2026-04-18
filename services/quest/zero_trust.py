"""Zero-trust inter-service authentication using HMAC-SHA256 tokens.

Vendored from shared/aethermoor_shared/auth.py — Docker build context for each
service only includes the service directory, so shared code is vendored here.
"""
import hashlib
import hmac
import os
import time

from fastapi import Header, HTTPException, status

_SERVICE_TOKEN = os.environ.get("SERVICE_TOKEN", "")


class ServiceTokenError(Exception):
    pass


def _expected_digest(timestamp: int) -> str:
    """HMAC-SHA256(SERVICE_TOKEN, str(timestamp)) as hex."""
    return hmac.new(
        _SERVICE_TOKEN.encode("utf-8"),
        str(timestamp).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def make_service_token() -> str:
    """Generate a time-bound token for outgoing service-to-service calls (60 s window)."""
    ts = int(time.time()) // 60
    return f"{ts}:{_expected_digest(ts)}"


def verify_service_token_value(header_value: str | None) -> None:
    """Raise ServiceTokenError if the token is absent, malformed, expired, or invalid."""
    if not header_value:
        raise ServiceTokenError("Missing X-Service-Token header")
    try:
        ts_str, digest = header_value.split(":", 1)
        ts = int(ts_str)
    except ValueError:
        raise ServiceTokenError("Malformed X-Service-Token")

    now_bucket = int(time.time()) // 60
    if ts not in (now_bucket, now_bucket - 1):
        raise ServiceTokenError("X-Service-Token expired")

    if not hmac.compare_digest(digest, _expected_digest(ts)):
        raise ServiceTokenError("X-Service-Token invalid")


def require_service_token(x_service_token: str | None = Header(default=None)) -> None:
    """FastAPI dependency — reject requests without a valid X-Service-Token."""
    try:
        verify_service_token_value(x_service_token)
    except ServiceTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
