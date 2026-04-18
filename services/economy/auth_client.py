"""HTTP client for verifying user JWTs with the Auth Service."""
import os

import httpx

from zero_trust import make_service_token

_AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://auth:8001")


class AuthVerificationError(Exception):
    pass


async def verify_user_jwt(token: str) -> dict:
    """Verify a user JWT with the Auth Service.

    Returns dict with {user_id, username} on success.
    Raises AuthVerificationError if the token is invalid.
    """
    service_token = make_service_token()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{_AUTH_SERVICE_URL}/auth/verify-service-token",
                json={"token": token},
                headers={"X-Service-Token": service_token},
            )
    except httpx.RequestError as exc:
        raise AuthVerificationError(f"Auth service unreachable: {exc}") from exc

    if response.status_code != 200:
        raise AuthVerificationError("Auth service returned unexpected status")

    data = response.json()
    if not data.get("valid"):
        raise AuthVerificationError("Invalid or expired token")

    return {
        "user_id": data["user_id"],
        "username": data["username"],
    }
