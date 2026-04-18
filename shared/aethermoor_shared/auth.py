"""Zero-trust inter-service authentication using HMAC-SHA256 tokens.

Each service receives SERVICE_TOKEN from the environment. Outgoing calls
include the header X-Service-Token. Receiving services validate with this
module before processing any request.
"""
import hashlib
import hmac
import os
import time

_TOKEN = os.environ.get("SERVICE_TOKEN", "")


class ServiceTokenError(Exception):
    pass


def _expected_token(timestamp: int) -> str:
    """Compute HMAC-SHA256(SECRET, str(timestamp)) as hex digest."""
    return hmac.new(
        _TOKEN.encode(),
        str(timestamp).encode(),
        hashlib.sha256,
    ).hexdigest()


def make_service_token() -> str:
    """Generate a time-bound token for outgoing service calls (60 s window)."""
    ts = int(time.time()) // 60  # 60-second epoch bucket
    return f"{ts}:{_expected_token(ts)}"


def verify_service_token(header_value: str | None) -> None:
    """Raise ServiceTokenError if the token is absent or invalid.

    Accepts tokens from the current 60-second bucket or the previous one to
    allow for clock skew between containers.
    """
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

    expected = _expected_token(ts)
    if not hmac.compare_digest(digest, expected):
        raise ServiceTokenError("X-Service-Token invalid")
